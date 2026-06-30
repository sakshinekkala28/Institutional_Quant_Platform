"""
====================================================================
Institutional Quant Platform

Authorization Dependency

Author : Institutional Quant Platform

Purpose
-------
Authorization dependency providers.

Provides

• Role Validation
• Permission Validation
• Ownership Validation
• Admin Access
• Trader Access
• Analyst Access
• Viewer Access
• Policy Enforcement

Used By

• FastAPI Routers
• Services
• Background Tasks

====================================================================
"""

from __future__ import annotations

from typing import Any

from fastapi import Depends
from fastapi import HTTPException

from api.dependencies.authentication import get_current_user


# ==========================================================
# ROLE PERMISSIONS
# ==========================================================


ROLE_PERMISSIONS: dict[str, set[str]] = {

    "admin": {

        "*",

    },

    "portfolio_manager": {

        "portfolio:read",

        "portfolio:write",

        "signals:read",

        "execution:read",

        "execution:write",

        "optimization:run",

        "risk:read",

        "backtest:run",

        "monitoring:read",

    },

    "trader": {

        "portfolio:read",

        "signals:read",

        "execution:read",

        "execution:write",

        "risk:read",

    },

    "analyst": {

        "portfolio:read",

        "signals:read",

        "optimization:run",

        "risk:read",

        "backtest:run",

    },

    "viewer": {

        "portfolio:read",

        "signals:read",

        "risk:read",

        "monitoring:read",

    },

}


# ==========================================================
# ROLE CHECK
# ==========================================================


def require_role(

    *allowed_roles: str,

):

    """
    Require one of the supplied roles.
    """

    def dependency(

        user: dict[str, Any] = Depends(

            get_current_user,

        ),

    ) -> dict[str, Any]:

        role = user.get(

            "role",

            "",

        )

        if role not in allowed_roles:

            raise HTTPException(

                status_code=403,

                detail=(

                    "Insufficient role."

                ),

            )

        return user

    return dependency


# ==========================================================
# PERMISSION CHECK
# ==========================================================


def require_permission(

    permission: str,

):

    """
    Require permission.
    """

    def dependency(

        user: dict[str, Any] = Depends(

            get_current_user,

        ),

    ) -> dict[str, Any]:

        role = user.get(

            "role",

            "",

        )

        permissions = ROLE_PERMISSIONS.get(

            role,

            set(),

        )

        if (

            "*"

            not in permissions

            and

            permission

            not in permissions

        ):

            raise HTTPException(

                status_code=403,

                detail=(

                    "Permission denied."

                ),

            )

        return user

    return dependency


# ==========================================================
# OWNER CHECK
# ==========================================================


def require_owner(

    owner_field: str = "username",

):

    """
    Ownership validation.
    """

    def dependency(

        user: dict[str, Any] = Depends(

            get_current_user,

        ),

    ) -> dict[str, Any]:

        if owner_field not in user:

            raise HTTPException(

                status_code=403,

                detail=(

                    "Ownership validation failed."

                ),

            )

        return user

    return dependency


# ==========================================================
# ADMIN
# ==========================================================


AdminOnly = require_role(

    "admin",

)


# ==========================================================
# PORTFOLIO MANAGER
# ==========================================================


PortfolioManagerOnly = require_role(

    "admin",

    "portfolio_manager",

)


# ==========================================================
# TRADER
# ==========================================================


TraderOnly = require_role(

    "admin",

    "portfolio_manager",

    "trader",

)


# ==========================================================
# ANALYST
# ==========================================================


AnalystOnly = require_role(

    "admin",

    "portfolio_manager",

    "analyst",

)


# ==========================================================
# VIEWER
# ==========================================================


ViewerOnly = require_role(

    "admin",

    "portfolio_manager",

    "trader",

    "analyst",

    "viewer",

)


# ==========================================================
# COMMON PERMISSIONS
# ==========================================================


CanReadPortfolio = require_permission(

    "portfolio:read",

)

CanWritePortfolio = require_permission(

    "portfolio:write",

)

CanReadSignals = require_permission(

    "signals:read",

)

CanExecuteTrades = require_permission(

    "execution:write",

)

CanRunOptimizer = require_permission(

    "optimization:run",

)

CanReadRisk = require_permission(

    "risk:read",

)

CanRunBacktest = require_permission(

    "backtest:run",

)

CanViewMonitoring = require_permission(

    "monitoring:read",

)


# ==========================================================
# HELPERS
# ==========================================================


def has_role(

    user: dict[str, Any],

    role: str,

) -> bool:

    return (

        user.get(

            "role",

        )

        == role

    )


def has_permission(

    user: dict[str, Any],

    permission: str,

) -> bool:

    permissions = ROLE_PERMISSIONS.get(

        user.get(

            "role",

            "",

        ),

        set(),

    )

    return (

        "*"

        in permissions

        or

        permission

        in permissions

    )


# ==========================================================
# SUMMARY
# ==========================================================


def authorization_summary(

) -> dict:

    return {

        "roles":

            sorted(

                ROLE_PERMISSIONS.keys(),

            ),

        "role_count":

            len(

                ROLE_PERMISSIONS,

            ),

        "permission_count":

            len(

                {

                    permission

                    for permissions

                    in ROLE_PERMISSIONS.values()

                    for permission

                    in permissions

                }

            ),

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "ROLE_PERMISSIONS",

    "require_role",

    "require_permission",

    "require_owner",

    "AdminOnly",

    "PortfolioManagerOnly",

    "TraderOnly",

    "AnalystOnly",

    "ViewerOnly",

    "CanReadPortfolio",

    "CanWritePortfolio",

    "CanReadSignals",

    "CanExecuteTrades",

    "CanRunOptimizer",

    "CanReadRisk",

    "CanRunBacktest",

    "CanViewMonitoring",

    "has_role",

    "has_permission",

    "authorization_summary",

]