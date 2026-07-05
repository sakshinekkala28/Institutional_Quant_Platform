"""
======================================================================

Institutional Quant Platform

Governance Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Governance & Compliance Service.

Responsibilities
----------------
• Investment Policy Enforcement
• Compliance Monitoring
• Risk Limit Governance
• Approval Workflow
• Audit Integration
• Regulatory Controls
• Governance Reporting

======================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from threading import Lock
from threading import RLock

from typing import Any
from typing import Dict
from typing import Callable
from typing import Optional

from core.services.base_service import BaseService


# ============================================================
# Exceptions
# ============================================================

class GovernanceError(Exception):
    """Base governance exception."""


class GovernanceProfileNotFound(GovernanceError):
    """Governance profile not found."""


class GovernanceEngineNotFound(GovernanceError):
    """Governance engine not registered."""


# ============================================================
# Governance Profile
# ============================================================

@dataclass(slots=True)
class GovernanceProfile:

    name: str

    policy: str

    owner: str

    parameters: Dict[str, Any] = field(

        default_factory=dict

    )

    metadata: Dict[str, Any] = field(

        default_factory=dict

    )

    created_at: datetime = field(

        default_factory=datetime.utcnow

    )


# ============================================================
# Governance Service
# ============================================================

class GovernanceService(BaseService):

    """
    Enterprise Governance Manager.
    """

    _instance = None

    _instance_lock = Lock()

    def __new__(

        cls,

        *args,

        **kwargs

    ):

        if cls._instance is None:

            with cls._instance_lock:

                if cls._instance is None:

                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(

        self

    ):

        if getattr(

            self,

            "_initialized",

            False

        ):

            return

        super().__init__()

        self._lock = RLock()

        self._profiles: Dict[str, GovernanceProfile] = {}

        self._engines: Dict[str, Callable] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info(

            "GovernanceService initialized."

        )

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(

        self

    ):

        self._enabled = True

    def disable(

        self

    ):

        self._enabled = False

    def enabled(

        self

    ):

        return self._enabled

    # =====================================================
    # Registration
    # =====================================================

    def register(

        self,

        name: str,

        policy: str,

        owner: str,

        parameters: Optional[Dict[str, Any]] = None,

        metadata: Optional[Dict[str, Any]] = None

    ) -> None:
        """
        Register governance profile.
        """

        profile = GovernanceProfile(

            name=name,

            policy=policy,

            owner=owner,

            parameters=parameters or {},

            metadata=metadata or {}

        )

        with self._lock:

            self._profiles[name] = profile

    # =====================================================
    # Governance Engine
    # =====================================================

    def register_engine(

        self,

        name: str,

        engine: Callable

    ) -> None:
        """
        Register governance engine.
        """

        self._engines[name] = engine

    # =====================================================
    # Retrieval
    # =====================================================

    def get(

        self,

        profile: str

    ) -> GovernanceProfile:

        if profile not in self._profiles:

            raise GovernanceProfileNotFound(

                profile

            )

        return self._profiles[profile]

    # =====================================================
    # BaseService
    # =====================================================

    def run(

        self

    ):

        return self.statistics()
    
    # =====================================================
    # Parameter Management
    # =====================================================

    def update_parameter(

        self,

        profile: str,

        name: str,

        value: Any

    ) -> None:
        """
        Update governance parameter.
        """

        self.get(

            profile

        ).parameters[name] = value

    def parameter(

        self,

        profile: str,

        name: str,

        default: Any = None

    ) -> Any:
        """
        Return governance parameter.
        """

        return self.get(

            profile

        ).parameters.get(

            name,

            default

        )

    # =====================================================
    # Governance Engine Execution
    # =====================================================

    def execute(

        self,

        profile: str,

        engine: str,

        *args,

        **kwargs

    ):
        """
        Execute governance engine.
        """

        if engine not in self._engines:

            raise GovernanceEngineNotFound(

                engine

            )

        governance_engine = self._engines[

            engine

        ]

        return governance_engine(

            profile=self.get(

                profile

            ),

            *args,

            **kwargs

        )

    # =====================================================
    # Compliance
    # =====================================================

    def compliance_check(

        self,

        profile: str,

        *args,

        **kwargs

    ):

        return self.execute(

            profile,

            "compliance",

            *args,

            **kwargs

        )

    # =====================================================
    # Policy Enforcement
    # =====================================================

    def policy_validation(

        self,

        profile: str,

        *args,

        **kwargs

    ):

        return self.execute(

            profile,

            "policy_validation",

            *args,

            **kwargs

        )

    # =====================================================
    # Risk Governance
    # =====================================================

    def risk_limit_validation(

        self,

        profile: str,

        *args,

        **kwargs

    ):

        return self.execute(

            profile,

            "risk_validation",

            *args,

            **kwargs

        )

    # =====================================================
    # Approval Workflow
    # =====================================================

    def approval(

        self,

        profile: str,

        *args,

        **kwargs

    ):

        return self.execute(

            profile,

            "approval",

            *args,

            **kwargs

        )

    # =====================================================
    # Audit
    # =====================================================

    def audit(

        self,

        profile: str,

        *args,

        **kwargs

    ):

        return self.execute(

            profile,

            "audit",

            *args,

            **kwargs

        )

    # =====================================================
    # Regulatory Reporting
    # =====================================================

    def regulatory_reporting(

        self,

        profile: str,

        *args,

        **kwargs

    ):

        return self.execute(

            profile,

            "regulatory_reporting",

            *args,

            **kwargs

        )

    # =====================================================
    # Validation
    # =====================================================

    def validate(

        self,

        profile: str

    ) -> bool:
        """
        Validate governance profile.
        """

        governance = self.get(

            profile

        )

        if not governance.policy:

            raise GovernanceError(

                "Policy is required."

            )

        if not governance.owner:

            raise GovernanceError(

                "Owner is required."

            )

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(

        self

    ) -> Dict[str, Any]:
        """
        Governance statistics.
        """

        return {

            "profiles":

                len(

                    self._profiles

                ),

            "engines":

                len(

                    self._engines

                ),

            "enabled":

                self._enabled

        }
    
    # =====================================================
    # Metadata
    # =====================================================

    def metadata(

        self,

        profile: str

    ) -> Dict[str, Any]:
        """
        Return governance metadata.
        """

        return dict(

            self.get(

                profile

            ).metadata

        )

    def update_metadata(

        self,

        profile: str,

        **kwargs

    ) -> None:
        """
        Update governance metadata.
        """

        self.get(

            profile

        ).metadata.update(

            kwargs

        )

    # =====================================================
    # Registry
    # =====================================================

    def exists(

        self,

        profile: str

    ) -> bool:
        """
        Check whether governance profile exists.
        """

        return profile in self._profiles

    def names(

        self

    ) -> list[str]:
        """
        Return registered governance profiles.
        """

        return sorted(

            self._profiles.keys()

        )

    def remove(

        self,

        profile: str

    ) -> None:
        """
        Remove governance profile.
        """

        if profile not in self._profiles:

            raise GovernanceProfileNotFound(

                profile

            )

        del self._profiles[

            profile

        ]

    def clear(

        self

    ) -> None:
        """
        Remove every governance profile
        and registered engine.
        """

        self._profiles.clear()

        self._engines.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(

        self,

        profile: str

    ) -> Dict[str, Any]:
        """
        Governance profile snapshot.
        """

        governance = self.get(

            profile

        )

        return {

            "name":

                governance.name,

            "policy":

                governance.policy,

            "owner":

                governance.owner,

            "parameters":

                dict(

                    governance.parameters

                ),

            "metadata":

                dict(

                    governance.metadata

                ),

            "created_at":

                governance.created_at.isoformat()

        }

    # =====================================================
    # Health
    # =====================================================

    def health(

        self

    ) -> Dict[str, Any]:
        """
        Governance service health.
        """

        return {

            "status":

                "HEALTHY"

                if self._enabled

                else "DISABLED",

            "enabled":

                self._enabled,

            "profiles":

                len(

                    self._profiles

                ),

            "engines":

                len(

                    self._engines

                )

        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(

        self

    ) -> None:

        self.enable()

        self._logger.info(

            "GovernanceService started."

        )

    def shutdown(

        self

    ) -> None:

        self.clear()

        self.disable()

        self._logger.info(

            "GovernanceService shutdown."

        )

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(

        self,

        profile: str

    ) -> bool:

        return self.exists(

            profile

        )

    def __len__(

        self

    ) -> int:

        return len(

            self._profiles

        )

    def __iter__(

        self

    ):

        return iter(

            self._profiles.items()

        )

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}"

            f"(profiles={len(self)}, "

            f"engines={len(self._engines)}, "

            f"enabled={self._enabled})"

        )


# ============================================================
# Global Singleton
# ============================================================

governance_service = GovernanceService()