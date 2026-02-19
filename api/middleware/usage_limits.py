"""
PATH: api/middleware/usage_limits.py
PURPOSE: Per-account usage tracking and enforcement.

Tracks API calls per user with daily and monthly caps. Expensive endpoints
(simulation, evolution, chat/LLM) consume more tokens than simple reads.

Tiers:
  - free (default):  500 tokens/day,  5,000/month
  - researcher:    2,000 tokens/day, 30,000/month
  - admin:         unlimited

Usage data is persisted to data/usage.json so it survives restarts.
"""

import json
import os
import threading
import time
from datetime import datetime, date
from functools import wraps
from typing import Any, Dict, Optional, Tuple

from flask import request, jsonify, g

# ── Configuration ──────────────────────────────────────────────
USAGE_TIERS = {
    "free": {
        "daily_tokens": int(os.environ.get("FREE_DAILY_TOKENS", "500")),
        "monthly_tokens": int(os.environ.get("FREE_MONTHLY_TOKENS", "5000")),
    },
    "user": {
        "daily_tokens": int(os.environ.get("USER_DAILY_TOKENS", "500")),
        "monthly_tokens": int(os.environ.get("USER_MONTHLY_TOKENS", "5000")),
    },
    "researcher": {
        "daily_tokens": int(os.environ.get("RESEARCHER_DAILY_TOKENS", "2000")),
        "monthly_tokens": int(os.environ.get("RESEARCHER_MONTHLY_TOKENS", "30000")),
    },
    "admin": {
        "daily_tokens": 999_999_999,
        "monthly_tokens": 999_999_999,
    },
}

# How many tokens each endpoint category costs
ENDPOINT_COSTS = {
    "/api/v1/simulate": 10,
    "/api/v1/evolution/evolve": 20,
    "/api/v1/evolution/analyze": 5,
    "/api/v1/agents/": 15,
    "/api/v1/reasoning/": 5,
    "/api/v1/equational/": 3,
    "/api/v1/brain/": 5,
    "/api/v1/vector/": 2,
    "/api/v1/substrate/chat": 25,
    "/api/v1/substrate/solve": 15,
    "/api/v1/substrate/discover": 20,
}
DEFAULT_COST = 1  # simple GET requests

# ── Persistent usage store ─────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_USAGE_FILE = os.path.join(_PROJECT_ROOT, "data", "usage.json")
_usage_lock = threading.Lock()


def _load_usage() -> Dict[str, Any]:
    try:
        if os.path.exists(_USAGE_FILE):
            with open(_USAGE_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_usage(data: Dict[str, Any]) -> None:
    try:
        os.makedirs(os.path.dirname(_USAGE_FILE), exist_ok=True)
        with open(_USAGE_FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"[usage] Warning: could not save usage file: {e}")


_usage_data: Dict[str, Any] = _load_usage()


def _get_user_usage(user_id: str) -> Dict[str, Any]:
    """Get or initialize usage record for a user."""
    today = date.today().isoformat()
    month = today[:7]  # YYYY-MM

    with _usage_lock:
        if user_id not in _usage_data:
            _usage_data[user_id] = {
                "daily": {"date": today, "tokens": 0},
                "monthly": {"month": month, "tokens": 0},
                "total_tokens": 0,
                "total_requests": 0,
            }

        record = _usage_data[user_id]

        # Reset daily counter if date changed
        if record["daily"]["date"] != today:
            record["daily"] = {"date": today, "tokens": 0}

        # Reset monthly counter if month changed
        if record["monthly"]["month"] != month:
            record["monthly"] = {"month": month, "tokens": 0}

        return record


def _get_endpoint_cost(path: str) -> int:
    """Determine the token cost for the given endpoint."""
    for prefix, cost in ENDPOINT_COSTS.items():
        if path.startswith(prefix):
            return cost
    return DEFAULT_COST


def check_usage(user_id: str, role: str, cost: int = 0) -> Tuple[bool, str, Dict]:
    """
    Check if user has remaining quota.
    Returns (allowed, message, usage_info).
    """
    tier = USAGE_TIERS.get(role, USAGE_TIERS["free"])
    record = _get_user_usage(user_id)

    daily_remaining = tier["daily_tokens"] - record["daily"]["tokens"]
    monthly_remaining = tier["monthly_tokens"] - record["monthly"]["tokens"]

    info = {
        "daily_used": record["daily"]["tokens"],
        "daily_limit": tier["daily_tokens"],
        "daily_remaining": max(0, daily_remaining),
        "monthly_used": record["monthly"]["tokens"],
        "monthly_limit": tier["monthly_tokens"],
        "monthly_remaining": max(0, monthly_remaining),
        "total_tokens": record["total_tokens"],
        "total_requests": record["total_requests"],
        "tier": role,
    }

    if daily_remaining < cost:
        return False, f"Daily limit reached ({tier['daily_tokens']} tokens/day). Resets at midnight UTC.", info

    if monthly_remaining < cost:
        return False, f"Monthly limit reached ({tier['monthly_tokens']} tokens/month). Resets next month.", info

    return True, "OK", info


def record_usage(user_id: str, cost: int) -> None:
    """Record token consumption for a user."""
    record = _get_user_usage(user_id)

    with _usage_lock:
        record["daily"]["tokens"] += cost
        record["monthly"]["tokens"] += cost
        record["total_tokens"] += cost
        record["total_requests"] += 1
        _save_usage(_usage_data)


def get_usage_summary(user_id: str, role: str) -> Dict:
    """Get a user's usage summary (for the /usage endpoint)."""
    _, _, info = check_usage(user_id, role, cost=0)
    return info


# ── Flask middleware & decorator ───────────────────────────────

def require_quota(extra_cost: int = 0):
    """
    Decorator that checks user quota before allowing the request.
    Must be placed AFTER @require_auth so g.current_user is set.

    Usage:
        @app.route("/api/v1/simulate")
        @require_auth
        @require_quota(extra_cost=10)
        def simulate():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user:
                return jsonify({"success": False, "error": "Authentication required"}), 401

            user_id = user.get("id", "anon")
            role = user.get("role", "free")
            path_cost = _get_endpoint_cost(request.path)
            cost = max(path_cost, extra_cost)

            allowed, message, info = check_usage(user_id, role, cost)

            if not allowed:
                resp = jsonify({
                    "success": False,
                    "error": message,
                    "usage": info,
                })
                resp.status_code = 429
                resp.headers["X-Usage-Daily-Remaining"] = str(info["daily_remaining"])
                resp.headers["X-Usage-Monthly-Remaining"] = str(info["monthly_remaining"])
                return resp

            # Allowed — record usage and proceed
            record_usage(user_id, cost)

            response = f(*args, **kwargs)

            # Attach usage headers
            if hasattr(response, "headers"):
                response.headers["X-Usage-Daily-Remaining"] = str(max(0, info["daily_remaining"] - cost))
                response.headers["X-Usage-Monthly-Remaining"] = str(max(0, info["monthly_remaining"] - cost))

            return response
        return decorated
    return decorator


class UsageLimitMiddleware:
    """
    Global middleware that enforces per-user usage limits on authenticated
    write/compute endpoints. Read-only GET endpoints on non-expensive paths
    are free.
    """

    @staticmethod
    def setup(app) -> None:
        @app.before_request
        def _check_usage_limits():
            # Skip non-authenticated, read-only, and free endpoints
            if request.method == "GET":
                return None
            if request.path.startswith(("/health", "/metrics", "/api/docs", "/api/openapi")):
                return None
            if request.path.startswith("/api/v1/auth/"):
                return None
            if request.path.startswith("/api/v1/changelog"):
                return None

            user = getattr(g, "current_user", None)
            if not user:
                return None  # Let auth middleware handle it

            user_id = user.get("id", "anon")
            role = user.get("role", "free")
            cost = _get_endpoint_cost(request.path)

            allowed, message, info = check_usage(user_id, role, cost)

            if not allowed:
                return (
                    jsonify({
                        "success": False,
                        "error": message,
                        "usage": info,
                    }),
                    429,
                    {
                        "X-Usage-Daily-Remaining": "0",
                        "X-Usage-Monthly-Remaining": str(info["monthly_remaining"]),
                    },
                )

            # Record usage
            record_usage(user_id, cost)
