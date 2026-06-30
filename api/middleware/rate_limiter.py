"""
====================================================================
Institutional Quant Platform

Rate Limiter Middleware

Author : Institutional Quant Platform

Purpose
-------
Institutional-grade rate limiting middleware.

Features

• IP Rate Limiting
• User Rate Limiting
• API Key Rate Limiting
• Sliding Window
• Rate Limit Headers
• Retry-After Header
• In-Memory Store
• Redis Ready

Used By

• FastAPI
• Authentication Middleware
• API Gateway

====================================================================
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# ==========================================================
# RATE LIMITER
# ==========================================================


class RateLimiter:
    """
    Sliding window rate limiter.
    """

    def __init__(

        self,

        requests: int = 100,

        window_seconds: int = 60,

    ):

        self.requests = requests

        self.window = window_seconds

        self.storage = defaultdict(

            deque,

        )

    # =====================================================
    # ALLOW
    # =====================================================

    def allow(

        self,

        key: str,

    ) -> tuple[bool, int]:

        now = time.time()

        queue = self.storage[key]

        while (

            queue

            and

            queue[0]

            <=

            now - self.window

        ):

            queue.popleft()

        if (

            len(queue)

            >=

            self.requests

        ):

            retry_after = int(

                self.window

                -

                (

                    now

                    -

                    queue[0]

                )

            )

            return (

                False,

                max(

                    retry_after,

                    1,

                ),

            )

        queue.append(

            now,

        )

        return (

            True,

            0,

        )

    # =====================================================
    # REMAINING
    # =====================================================

    def remaining(

        self,

        key: str,

    ) -> int:

        now = time.time()

        queue = self.storage[key]

        while (

            queue

            and

            queue[0]

            <=

            now - self.window

        ):

            queue.popleft()

        return max(

            self.requests

            -

            len(queue),

            0,

        )


# ==========================================================
# MIDDLEWARE
# ==========================================================


class RateLimitMiddleware(
    BaseHTTPMiddleware,
):
    """
    Rate limiting middleware.
    """

    def __init__(

        self,

        app,

        requests: int = 100,

        window_seconds: int = 60,

    ):

        super().__init__(

            app,

        )

        self.limiter = RateLimiter(

            requests,

            window_seconds,

        )

    # =====================================================
    # DISPATCH
    # =====================================================

    async def dispatch(

        self,

        request: Request,

        call_next: Callable,

    ):

        api_key = request.headers.get(

            "X-API-Key",

        )

        user = getattr(

            request.state,

            "user",

            None,

        )

        if api_key:

            key = f"apikey:{api_key}"

        elif user:

            key = (

                f"user:"

                f"{user.get('username')}"

            )

        else:

            client = (

                request.client.host

                if request.client

                else "unknown"

            )

            key = f"ip:{client}"

        allowed, retry = (

            self.limiter.allow(

                key,

            )

        )

        if not allowed:

            return JSONResponse(

                status_code=429,

                headers={

                    "Retry-After":

                        str(

                            retry,

                        ),

                    "X-RateLimit-Limit":

                        str(

                            self.limiter.requests,

                        ),

                    "X-RateLimit-Remaining":

                        "0",

                },

                content={

                    "success":

                        False,

                    "error":

                        "Rate limit exceeded",

                    "retry_after":

                        retry,

                },

            )

        response = await call_next(

            request,

        )

        response.headers[

            "X-RateLimit-Limit"

        ] = str(

            self.limiter.requests,

        )

        response.headers[

            "X-RateLimit-Remaining"

        ] = str(

            self.limiter.remaining(

                key,

            )

        )

        response.headers[

            "X-RateLimit-Window"

        ] = str(

            self.limiter.window,

        )

        return response


# ==========================================================
# FACTORY
# ==========================================================


def create_rate_limiter(

    requests: int = 100,

    window_seconds: int = 60,

) -> RateLimitMiddleware:
    """
    Factory function.
    """

    return RateLimitMiddleware(

        app=None,

        requests=requests,

        window_seconds=window_seconds,

    )


# ==========================================================
# SUMMARY
# ==========================================================


def rate_limit_summary(

    limiter: RateLimiter,

) -> dict:

    return {

        "requests":

            limiter.requests,

        "window_seconds":

            limiter.window,

        "tracked_clients":

            len(

                limiter.storage,

            ),

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "RateLimiter",

    "RateLimitMiddleware",

    "create_rate_limiter",

    "rate_limit_summary",

]