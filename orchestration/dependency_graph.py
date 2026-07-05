"""
Institutional Quant Platform
============================

Dependency Graph

Builds and validates the execution DAG for all registered engines.

Responsibilities
----------------
- Build dependency graph
- Validate dependencies
- Detect circular dependencies
- Compute topological execution order
- Determine executable stages

Author: Institutional Quant Platform
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, List, Set

from orchestration.engine_registry import EngineRegistry


class DependencyGraph:
    """
    Directed Acyclic Graph (DAG) of engine dependencies.
    """

    def __init__(self, registry: EngineRegistry):

        self.registry = registry

        self.graph: Dict[str, List[str]] = defaultdict(list)

        self.reverse_graph: Dict[str, List[str]] = defaultdict(list)

        self.indegree: Dict[str, int] = defaultdict(int)

        self._build()

    # ------------------------------------------------------------------

    def _build(self):

        metadata = self.registry.metadata()

        # initialize

        for engine in metadata:

            self.indegree[engine] = 0

        # build graph

        for engine, info in metadata.items():

            for dependency in info["depends_on"]:

                if dependency not in metadata:

                    raise ValueError(
                        f"{engine} depends on unknown engine '{dependency}'"
                    )

                self.graph[dependency].append(engine)

                self.reverse_graph[engine].append(dependency)

                self.indegree[engine] += 1

    # ------------------------------------------------------------------

    def execution_order(self) -> List[str]:
        """
        Topological sort using Kahn's algorithm.
        """

        indegree = dict(self.indegree)

        queue = deque(
            sorted(
                [
                    node
                    for node, degree in indegree.items()
                    if degree == 0
                ]
            )
        )

        order = []

        while queue:

            node = queue.popleft()

            order.append(node)

            for child in sorted(self.graph[node]):

                indegree[child] -= 1

                if indegree[child] == 0:

                    queue.append(child)

        if len(order) != len(indegree):

            raise RuntimeError(
                "Circular dependency detected in pipeline."
            )

        return order

    # ------------------------------------------------------------------

    def stages(self) -> List[List[str]]:
        """
        Returns engines grouped into executable parallel stages.
        """

        indegree = dict(self.indegree)

        stages = []

        remaining = set(indegree.keys())

        while remaining:

            ready = sorted(
                [
                    node
                    for node in remaining
                    if indegree[node] == 0
                ]
            )

            if not ready:

                raise RuntimeError(
                    "Circular dependency detected."
                )

            stages.append(ready)

            for node in ready:

                remaining.remove(node)

                for child in self.graph[node]:

                    indegree[child] -= 1

        return stages

    # ------------------------------------------------------------------

    def downstream(self, engine: str) -> List[str]:
        """
        Returns engines depending on this engine.
        """

        return sorted(self.graph.get(engine, []))

    # ------------------------------------------------------------------

    def upstream(self, engine: str) -> List[str]:
        """
        Returns dependencies of this engine.
        """

        return sorted(self.reverse_graph.get(engine, []))

    # ------------------------------------------------------------------

    def validate(self) -> bool:

        self.execution_order()

        return True

    # ------------------------------------------------------------------

    def roots(self) -> List[str]:
        """
        Engines with no dependencies.
        """

        return sorted(
            [
                node
                for node, degree in self.indegree.items()
                if degree == 0
            ]
        )

    # ------------------------------------------------------------------

    def leaves(self) -> List[str]:
        """
        Engines with no dependents.
        """

        return sorted(
            [
                node
                for node in self.indegree
                if len(self.graph[node]) == 0
            ]
        )

    # ------------------------------------------------------------------

    def visualize(self):

        print("=" * 80)
        print("DEPENDENCY GRAPH")
        print("=" * 80)

        for engine in self.execution_order():

            deps = self.upstream(engine)

            if deps:

                print(
                    f"{engine:<35} ← {', '.join(deps)}"
                )

            else:

                print(
                    f"{engine:<35} ← ROOT"
                )

        print("=" * 80)

    # ------------------------------------------------------------------

    def summary(self):

        return {
            "engines": len(self.indegree),
            "roots": self.roots(),
            "leaves": self.leaves(),
            "execution_order": self.execution_order(),
            "parallel_stages": self.stages(),
        }

    # ------------------------------------------------------------------

    def __repr__(self):

        return (
            f"DependencyGraph("
            f"engines={len(self.indegree)})"
        )