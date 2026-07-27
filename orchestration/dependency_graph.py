"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Dependency Graph

Enterprise-grade Directed Acyclic Graph (DAG)
responsible for constructing, validating and
planning execution of all registered engines.

Responsibilities

• Build Dependency Graph
• Dependency Validation
• Cycle Detection
• Topological Sorting
• Parallel Stage Planning
• Critical Path Analysis
• Graph Metrics
• Execution Planning
• Graph Export

=========================================================
"""

from __future__ import annotations

from collections import defaultdict, deque

from orchestration.base_engine import (
    BaseEngine,
)
from orchestration.engine_registry import (
    EngineRegistry,
)


class DependencyGraph:
    """
    Directed Acyclic Graph (DAG)
    representing execution dependencies
    between all registered engines.

    Graph Direction

        Dependency
             │
             ▼

        Factor Engine
             │
             ▼

        Signal Engine
             │
             ▼

        Portfolio Engine

    Internally stored as

        Factor
            ─────► Signal

        Signal
            ─────► Portfolio
    """

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

    def __init__(
        self,
        registry: EngineRegistry,
    ) -> None:

        self.registry = registry

        # ---------------------------------------------
        # Forward Graph
        #
        # dependency -> dependents
        # ---------------------------------------------

        self._graph: dict[
            str,
            set[str],
        ] = defaultdict(set)

        # ---------------------------------------------
        # Reverse Graph
        #
        # engine -> dependencies
        # ---------------------------------------------

        self._reverse_graph: dict[
            str,
            set[str],
        ] = defaultdict(set)

        # ---------------------------------------------
        # Engine Registry Snapshot
        # ---------------------------------------------

        self._nodes: dict[
            str,
            type[BaseEngine],
        ] = {}

        # ---------------------------------------------
        # In-degree Cache
        # ---------------------------------------------

        self._indegree: dict[
            str,
            int,
        ] = defaultdict(int)

        # ---------------------------------------------
        # Build Status
        # ---------------------------------------------

        self._built = False

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def node_count(
        self,
    ) -> int:

        return len(self._nodes)

    # -----------------------------------------------------

    @property
    def edge_count(
        self,
    ) -> int:

        return sum(len(edges) for edges in self._graph.values())

    # -----------------------------------------------------

    @property
    def is_built(
        self,
    ) -> bool:

        return self._built

    # -----------------------------------------------------

    @property
    def nodes(
        self,
    ) -> list[str]:

        return sorted(self._nodes.keys())

    # -----------------------------------------------------

    @property
    def roots(
        self,
    ) -> list[str]:

        return sorted(
            [
                node
                for (
                    node,
                    degree,
                ) in self._indegree.items()
                if degree == 0
            ],
            key=lambda node: (
                self._nodes[node].PRIORITY,
                node,
            ),
        )

    # -----------------------------------------------------

    @property
    def leaves(
        self,
    ) -> list[str]:

        return sorted(
            [node for node in self._nodes if not self._graph[node]],
            key=lambda node: (
                self._nodes[node].PRIORITY,
                node,
            ),
        )

    # -----------------------------------------------------

    @property
    def isolated_nodes(
        self,
    ) -> list[str]:

        isolated = []

        for node in self._nodes:
            if not self._graph[node] and not self._reverse_graph[node]:
                isolated.append(node)

        return sorted(isolated)

    # =====================================================
    # BUILD GRAPH
    # =====================================================

    def build(self) -> None:
        """
        Build the dependency graph from the
        registered engines.
        """

        # ---------------------------------------------
        # Reset current graph
        # ---------------------------------------------

        self._graph.clear()

        self._reverse_graph.clear()

        self._nodes.clear()

        self._indegree.clear()

        # ---------------------------------------------
        # Register every engine
        # ---------------------------------------------

        for engine in self.registry.sorted_by_priority():
            self.add_node(engine)

        # ---------------------------------------------
        # Register dependencies
        # ---------------------------------------------

        for engine in self.registry.sorted_by_priority():
            for dependency in engine.DEPENDS_ON:
                self.add_dependency(
                    dependency,
                    engine.NAME,
                )

        self._built = True

    # =====================================================
    # REBUILD GRAPH
    # =====================================================

    def rebuild(self) -> None:
        """
        Rebuild graph from registry.
        """

        self.build()

    # =====================================================
    # ADD NODE
    # =====================================================

    def add_node(
        self,
        engine: type[BaseEngine],
    ) -> None:
        """
        Register an engine as a graph node.
        """

        if engine.NAME in self._nodes:
            return

        self._nodes[engine.NAME] = engine

        self._graph.setdefault(
            engine.NAME,
            set(),
        )

        self._reverse_graph.setdefault(
            engine.NAME,
            set(),
        )

        self._indegree.setdefault(
            engine.NAME,
            0,
        )

    # =====================================================
    # REMOVE NODE
    # =====================================================

    def remove_node(
        self,
        engine_name: str,
    ) -> None:
        """
        Remove an engine from the graph.
        """

        if engine_name not in self._nodes:
            return

        # ---------------------------------------------
        # Remove outgoing edges
        # ---------------------------------------------

        for child in list(self._graph[engine_name]):
            self.remove_dependency(
                engine_name,
                child,
            )

        # ---------------------------------------------
        # Remove incoming edges
        # ---------------------------------------------

        for parent in list(self._reverse_graph[engine_name]):
            self.remove_dependency(
                parent,
                engine_name,
            )

        # ---------------------------------------------
        # Remove node
        # ---------------------------------------------

        self._graph.pop(
            engine_name,
            None,
        )

        self._reverse_graph.pop(
            engine_name,
            None,
        )

        self._indegree.pop(
            engine_name,
            None,
        )

        self._nodes.pop(
            engine_name,
            None,
        )

    # =====================================================
    # ADD DEPENDENCY
    # =====================================================

    def add_dependency(
        self,
        dependency: str,
        engine: str,
    ) -> None:
        """
        Register a dependency.

        dependency ---> engine
        """

        if dependency not in self._nodes:
            raise KeyError(f"Unknown dependency '{dependency}'.")

        if engine not in self._nodes:
            raise KeyError(f"Unknown engine '{engine}'.")

        if engine in self._graph[dependency]:
            return

        self._graph[dependency].add(engine)

        self._reverse_graph[engine].add(dependency)

        self._indegree[engine] += 1

    # =====================================================
    # REMOVE DEPENDENCY
    # =====================================================

    def remove_dependency(
        self,
        dependency: str,
        engine: str,
    ) -> None:
        """
        Remove a dependency edge.
        """

        if dependency not in self._graph:
            return

        if engine not in self._graph[dependency]:
            return

        self._graph[dependency].remove(engine)

        self._reverse_graph[engine].remove(dependency)

        self._indegree[engine] -= 1

    # =====================================================
    # GRAPH RESET
    # =====================================================

    def clear(self) -> None:
        """
        Remove every node and edge.
        """

        self._graph.clear()

        self._reverse_graph.clear()

        self._nodes.clear()

        self._indegree.clear()

        self._built = False

    # =====================================================
    # NODE QUERIES
    # =====================================================

    def has_node(
        self,
        engine_name: str,
    ) -> bool:
        """
        Check whether a node exists.
        """

        return engine_name in self._nodes

    # -----------------------------------------------------

    def has_dependency(
        self,
        dependency: str,
        engine: str,
    ) -> bool:
        """
        Return True if

            dependency ---> engine

        exists.
        """

        return dependency in self._graph and engine in self._graph[dependency]

    # =====================================================
    # DIRECT RELATIONSHIPS
    # =====================================================

    def upstream(
        self,
        engine_name: str,
    ) -> list[str]:
        """
        Immediate dependencies.

        engine
            ↑
        dependencies
        """

        if not self.has_node(engine_name):
            raise KeyError(f"Unknown engine '{engine_name}'.")

        return sorted(
            self._reverse_graph[engine_name],
            key=lambda node: (
                self._nodes[node].PRIORITY,
                node,
            ),
        )

    # -----------------------------------------------------

    def downstream(
        self,
        engine_name: str,
    ) -> list[str]:
        """
        Immediate dependents.

        engine
            ↓
        dependents
        """

        if not self.has_node(engine_name):
            raise KeyError(f"Unknown engine '{engine_name}'.")

        return sorted(
            self._graph[engine_name],
            key=lambda node: (
                self._nodes[node].PRIORITY,
                node,
            ),
        )

    # =====================================================
    # RECURSIVE RELATIONSHIPS
    # =====================================================

    def ancestors(
        self,
        engine_name: str,
    ) -> list[str]:
        """
        Return every upstream dependency.
        """

        if not self.has_node(engine_name):
            raise KeyError(engine_name)

        visited: set[str] = set()

        def dfs(
            node: str,
        ) -> None:

            for parent in self._reverse_graph[node]:
                if parent in visited:
                    continue

                visited.add(parent)

                dfs(parent)

        dfs(engine_name)

        return sorted(
            visited,
            key=lambda node: (
                self._nodes[node].PRIORITY,
                node,
            ),
        )

    # -----------------------------------------------------

    def descendants(
        self,
        engine_name: str,
    ) -> list[str]:
        """
        Return every downstream engine.
        """

        if not self.has_node(engine_name):
            raise KeyError(engine_name)

        visited: set[str] = set()

        def dfs(
            node: str,
        ) -> None:

            for child in self._graph[node]:
                if child in visited:
                    continue

                visited.add(child)

                dfs(child)

        dfs(engine_name)

        return sorted(
            visited,
            key=lambda node: (
                self._nodes[node].PRIORITY,
                node,
            ),
        )

    # =====================================================
    # ALIASES
    # =====================================================

    def dependencies(
        self,
        engine_name: str,
    ) -> list[str]:
        """
        Alias for upstream().
        """

        return self.upstream(engine_name)

    # -----------------------------------------------------

    def dependents(
        self,
        engine_name: str,
    ) -> list[str]:
        """
        Alias for downstream().
        """

        return self.downstream(engine_name)

    # =====================================================
    # GRAPH INSPECTION
    # =====================================================

    def neighbors(
        self,
        engine_name: str,
    ) -> dict[
        str,
        list[str],
    ]:
        """
        Return adjacent nodes.
        """

        return {
            "upstream": self.upstream(engine_name),
            "downstream": self.downstream(engine_name),
        }

    # -----------------------------------------------------

    def degree(
        self,
        engine_name: str,
    ) -> dict[str, int]:
        """
        Return node degree.
        """

        return {
            "indegree": len(self._reverse_graph[engine_name]),
            "outdegree": len(self._graph[engine_name]),
            "total": len(self._reverse_graph[engine_name])
            + len(self._graph[engine_name]),
        }

    # -----------------------------------------------------

    def adjacency_list(
        self,
    ) -> dict[
        str,
        list[str],
    ]:
        """
        Return graph as an
        adjacency list.
        """

        return {
            node: sorted(
                children,
                key=lambda n: (
                    self._nodes[n].PRIORITY,
                    n,
                ),
            )
            for (
                node,
                children,
            ) in self._graph.items()
        }

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate_dependencies(
        self,
    ) -> list[str]:
        """
        Validate that every declared dependency
        exists inside the graph.
        """

        errors: list[str] = []

        for engine in self._nodes.values():
            for dependency in engine.DEPENDS_ON:
                if dependency not in self._nodes:
                    errors.append(
                        f"{engine.NAME} "
                        f"depends on "
                        f"'{dependency}' "
                        f"which is not "
                        f"registered."
                    )

        return errors

    # -----------------------------------------------------

    def validate_nodes(
        self,
    ) -> list[str]:
        """
        Validate node integrity.
        """

        errors: list[str] = []

        for node in self._nodes:
            if node not in self._graph:
                errors.append(f"Missing graph node '{node}'.")

            if node not in self._reverse_graph:
                errors.append(f"Missing reverse graph node '{node}'.")

        return errors

    # =====================================================
    # CYCLE DETECTION
    # =====================================================

    def detect_cycles(
        self,
    ) -> list[list[str]]:
        """
        Detect dependency cycles.

        Returns a list of cycles.
        """

        visited: set[str] = set()

        stack: set[str] = set()

        cycles: list[list[str]] = []

        path: list[str] = []

        def dfs(node: str) -> None:

            visited.add(node)

            stack.add(node)

            path.append(node)

            for child in self._graph[node]:
                if child not in visited:
                    dfs(child)

                elif child in stack:
                    try:
                        start = path.index(child)

                        cycles.append(path[start:] + [child])

                    except ValueError:
                        pass

            stack.remove(node)

            path.pop()

        for node in self._nodes:
            if node not in visited:
                dfs(node)

        return cycles

    # =====================================================
    # TOPOLOGICAL SORT
    # =====================================================

    def execution_order(
        self,
    ) -> list[str]:
        """
        Compute dependency order using
        Kahn's Algorithm.
        """

        indegree = dict(self._indegree)

        ready = deque(
            sorted(
                [node for node, degree in indegree.items() if degree == 0],
                key=lambda node: (
                    self._nodes[node].PRIORITY,
                    node,
                ),
            )
        )

        order: list[str] = []

        while ready:
            node = ready.popleft()

            order.append(node)

            children = sorted(
                self._graph[node],
                key=lambda child: (
                    self._nodes[child].PRIORITY,
                    child,
                ),
            )

            for child in children:
                indegree[child] -= 1

                if indegree[child] == 0:
                    ready.append(child)

        if len(order) != self.node_count:
            raise RuntimeError("Dependency graph contains one or more cycles.")

        return order

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(
        self,
    ) -> dict[str, object]:
        """
        Validate the complete graph.
        """

        dependency_errors = self.validate_dependencies()

        node_errors = self.validate_nodes()

        cycles = self.detect_cycles()

        return {
            "valid": (not dependency_errors and not node_errors and not cycles),
            "dependency_errors": dependency_errors,
            "node_errors": node_errors,
            "cycles": cycles,
        }

    # =====================================================
    # EXECUTION LEVELS
    # =====================================================

    def execution_levels(
        self,
    ) -> list[list[str]]:
        """
        Compute execution levels.

        Engines within the same level have
        no dependency on each other and may
        execute in parallel.
        """

        indegree = dict(self._indegree)

        remaining = set(self._nodes.keys())

        levels: list[list[str]] = []

        while remaining:
            ready = sorted(
                [node for node in remaining if indegree[node] == 0],
                key=lambda node: (
                    self._nodes[node].PRIORITY,
                    node,
                ),
            )

            if not ready:
                raise RuntimeError("Dependency cycle detected.")

            levels.append(ready)

            for node in ready:
                remaining.remove(node)

                for child in self._graph[node]:
                    indegree[child] -= 1

        return levels

    # =====================================================
    # EXECUTION PLAN
    # =====================================================

    def execution_plan(
        self,
    ) -> list[dict]:
        """
        Build execution plan suitable
        for the Pipeline Builder.
        """

        plan = []

        for level, engines in enumerate(
            self.execution_levels(),
            start=1,
        ):
            plan.append(
                {
                    "level": level,
                    "parallel": True,
                    "engine_count": len(engines),
                    "engines": engines,
                }
            )

        return plan

    # =====================================================
    # GRAPH METRICS
    # =====================================================

    def maximum_depth(
        self,
    ) -> int:
        """
        Maximum dependency depth.
        """

        return len(self.execution_levels())

    # -----------------------------------------------------

    def maximum_parallelism(
        self,
    ) -> int:
        """
        Largest number of engines that
        may execute concurrently.
        """

        return max(
            (len(level) for level in self.execution_levels()),
            default=0,
        )

    # -----------------------------------------------------

    def edge_density(
        self,
    ) -> float:
        """
        Directed graph density.
        """

        n = self.node_count

        if n <= 1:
            return 0.0

        maximum_edges = n * (n - 1)

        return round(
            self.edge_count / maximum_edges,
            4,
        )

    # -----------------------------------------------------

    def graph_metrics(
        self,
    ) -> dict[str, object]:
        """
        Return graph statistics.
        """

        return {
            "nodes": self.node_count,
            "edges": self.edge_count,
            "roots": len(self.roots),
            "leaves": len(self.leaves),
            "isolated": len(self.isolated_nodes),
            "depth": self.maximum_depth(),
            "parallelism": self.maximum_parallelism(),
            "density": self.edge_density(),
        }

    # =====================================================
    # CRITICAL PATH
    # =====================================================

    def critical_path(
        self,
    ) -> list[str]:
        """
        Approximate critical execution path.

        Currently returns the longest
        dependency chain based on execution
        levels.
        """

        levels = self.execution_levels()

        if not levels:
            return []

        path = []

        for level in levels:
            path.append(level[0])

        return path

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> dict[str, object]:
        """
        Export the graph as a serializable
        dictionary.
        """

        return {
            "nodes": sorted(self._nodes.keys()),
            "edges": {
                node: sorted(
                    children,
                    key=lambda n: (
                        self._nodes[n].PRIORITY,
                        n,
                    ),
                )
                for (
                    node,
                    children,
                ) in self._graph.items()
            },
            "metrics": self.graph_metrics(),
            "execution_plan": self.execution_plan(),
        }

    # -----------------------------------------------------

    def to_json(
        self,
        indent: int = 4,
    ) -> str:
        """
        Export graph as JSON.
        """

        import json

        return json.dumps(
            self.to_dict(),
            indent=indent,
        )

    # =====================================================
    # MERMAID EXPORT
    # =====================================================

    def to_mermaid(
        self,
    ) -> str:
        """
        Export graph in Mermaid format.
        """

        lines = [
            "graph TD",
        ]

        for (
            parent,
            children,
        ) in sorted(self._graph.items()):
            if not children:
                lines.append(f"    {parent}")

                continue

            for child in sorted(children):
                lines.append(f"    {parent} --> {child}")

        return "\n".join(lines)

    # =====================================================
    # ASCII EXPORT
    # =====================================================

    def to_ascii(
        self,
    ) -> str:
        """
        Human-readable graph.
        """

        lines = []

        for node in self.execution_order():
            deps = self.upstream(node)

            if deps:
                dependency_text = ", ".join(deps)

            else:
                dependency_text = "ROOT"

            lines.append(f"{node:<35}<-- {dependency_text}")

        return "\n".join(lines)

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict[str, object]:
        """
        Graph summary.
        """

        validation = self.validate()

        return {
            "built": self.is_built,
            "valid": validation["valid"],
            "metrics": self.graph_metrics(),
            "roots": self.roots,
            "leaves": self.leaves,
            "execution_order": self.execution_order(),
            "execution_levels": self.execution_levels(),
            "validation": validation,
        }

    # =====================================================
    # DUNDER METHODS
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return self.node_count

    # -----------------------------------------------------

    def __contains__(
        self,
        engine_name: str,
    ) -> bool:

        return self.has_node(engine_name)

    # -----------------------------------------------------

    def __iter__(
        self,
    ):

        return iter(self.execution_order())

    # -----------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"nodes={self.node_count}, "
            f"edges={self.edge_count}, "
            f"depth={self.maximum_depth()}, "
            f"built={self.is_built})"
        )
