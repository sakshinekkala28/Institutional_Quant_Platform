"""
====================================================================
Institutional Quant Platform

Authorization Middleware

Author : Institutional Quant Platform

Purpose
-------
Role-Based Access Control (RBAC) middleware.

Features

• Role Validation
• Permission Validation
• Admin Access
• Trader Access
• Read-Only Access
• Route Authorization

Used By

• Authentication Middleware
• All API Routers

====================================================================
"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import HTTPException
from fastapi import Request


# ==========================================================
# ROLE DEFINITIONS
# ==========================================================

ROLES = {

    "admin": {

        "*",

    },

    "portfolio_manager": {

        "portfolio:read",

        "portfolio:write",

        "signals:read",

        "execution:read",

        "execution:write",

        "risk:read",

        "optimization:run",

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

        "risk:read",

        "backtest:run",

        "optimization:run",

    },

    "viewer": {

        "portfolio:read",

        "signals:read",

        "risk:read",

        "monitoring:read",

    },

}


# ==========================================================
# PERMISSION CHECK
# ==========================================================


def has_permission(

    role: str,

    permission: str,

) -> bool:
    """
    Check whether a role has a permission.
    """

    permissions = ROLES.get(

        role,

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
# ROLE CHECK
# ==========================================================


def require_role(

    *roles: str,

):
    """
    Role validator.
    """

    async def dependency(

        request: Request,

    ):

        user = getattr(

            request.state,

            "user",

            None,

        )

        if user is None:

            raise HTTPException(

                status_code=401,

                detail="Authentication required.",

            )

        user_role = (

            user.get(

                "role",

                "",

            )

        )

        if user_role not in roles:

            raise HTTPException(

                status_code=403,

                detail="Access denied.",

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
    Permission validator.
    """

    async def dependency(

        request: Request,

    ):

        user = getattr(

            request.state,

            "user",

            None,

        )

        if user is None:

            raise HTTPException(

                status_code=401,

                detail="Authentication required.",

            )

        role = (

            user.get(

                "role",

                "",

            )

        )

        if not has_permission(

            role,

            permission,

        ):

            raise HTTPException(

                status_code=403,

                detail=(

                    "Insufficient permissions."

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

    "analyst",

    "viewer",

    "trader",

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

CanReadRisk = require_permission(

    "risk:read",

)

CanOptimize = require_permission(

    "optimization:run",

)

CanRunBacktest = require_permission(

    "backtest:run",

)

CanMonitor = require_permission(

    "monitoring:read",

)


# ==========================================================
# USER INFO
# ==========================================================


def current_role(

    request: Request,

) -> str:

    user = getattr(

        request.state,

        "user",

        None,

    )

    if user is None:

        return ""

    return user.get(

        "role",

        "",

    )


# ==========================================================
# AUTHORIZATION SUMMARY
# ==========================================================


def authorization_summary(

) -> dict:

    return {

        "roles":

            sorted(

                ROLES.keys(),

            ),

        "permissions":

            sum(

                len(v)

                for v

                in ROLES.values()

            ),

    }