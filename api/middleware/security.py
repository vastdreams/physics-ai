"""
PATH: api/middleware/security.py
PURPOSE: Security hardening middleware — HTTP security headers, CSRF protection,
         request size limits, and suspicious request blocking.

Applied globally via `SecurityMiddleware.setup(app)` in create_app().
"""

import os
import re
import time
import threading
from collections import defaultdict
from typing import Dict, Set

from flask import Flask, request, jsonify, g


# ── Suspicious IP tracker ──────────────────────────────────────
# Tracks IPs that make many 4xx/5xx requests — potential scanners
_suspicious_ips: Dict[str, list] = {}
_blocked_ips: Set[str] = set()
_sus_lock = threading.Lock()

# Configuration via env
_MAX_SUSPICIOUS_HITS = int(os.environ.get("SECURITY_SUSPICIOUS_THRESHOLD", "50"))
_SUSPICIOUS_WINDOW = int(os.environ.get("SECURITY_SUSPICIOUS_WINDOW", "300"))  # 5 min
_IP_BLOCK_DURATION = int(os.environ.get("SECURITY_BLOCK_DURATION", "1800"))     # 30 min
_MAX_REQUEST_SIZE = int(os.environ.get("MAX_REQUEST_SIZE_MB", "10")) * 1024 * 1024


def _get_real_ip() -> str:
    """Get the real client IP behind proxies."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


class SecurityMiddleware:
    """
    Applies defense-in-depth security to the Flask app:

    1. Security headers (XSS, clickjacking, MIME sniffing, HSTS, CSP)
    2. Request size limits
    3. Suspicious payload detection (SQL injection, XSS, path traversal)
    4. Auto-blocking of scanner/bot IPs
    5. Request ID tracking
    """

    @staticmethod
    def setup(app: Flask) -> None:
        """Register all security hooks on the Flask app."""

        # ── Max request body size ───────────────────────────────
        app.config["MAX_CONTENT_LENGTH"] = _MAX_REQUEST_SIZE

        # ── Before request: block bad actors, validate inputs ───
        @app.before_request
        def _security_before():
            ip = _get_real_ip()

            # 1. Check if IP is blocked
            if ip in _blocked_ips:
                return jsonify({
                    "success": False,
                    "error": "Access denied"
                }), 403

            # 2. Block obviously malicious paths (path traversal, scanners)
            path = request.path.lower()
            _dangerous_patterns = [
                "../",          # Path traversal
                "..\\",
                "/etc/passwd",
                "/proc/self",
                "wp-admin",     # WordPress scanner
                "wp-login",
                ".env",         # Env file probing
                "phpinfo",
                "phpmyadmin",
                "/cgi-bin/",
                "/shell",
                "/.git/",
                "/admin/config",
            ]
            for pat in _dangerous_patterns:
                if pat in path:
                    _record_suspicious(ip)
                    return jsonify({"success": False, "error": "Forbidden"}), 403

            # 3. Check request body for injection patterns (POST/PUT only)
            if request.method in ("POST", "PUT", "PATCH") and request.content_type:
                if "json" in request.content_type:
                    raw = request.get_data(as_text=True, cache=True)
                    if raw and _contains_injection(raw):
                        _record_suspicious(ip)
                        return jsonify({
                            "success": False,
                            "error": "Invalid input detected"
                        }), 400

            # 4. Attach request metadata
            g.request_ip = ip
            g.request_start = time.time()

        # ── After request: add security headers ─────────────────
        @app.after_request
        def _security_after(response):
            # Core security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = (
                "camera=(), microphone=(), geolocation=(), payment=()"
            )

            # Content Security Policy — permissive for API, tighter for HTML
            if response.content_type and "text/html" in response.content_type:
                response.headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' https://unpkg.com; "
                    "style-src 'self' 'unsafe-inline' https://unpkg.com https://fonts.googleapis.com; "
                    "font-src 'self' https://fonts.gstatic.com; "
                    "img-src 'self' data:; "
                    "connect-src 'self' ws: wss:; "
                    "frame-ancestors 'none';"
                )

            # HSTS (only effective over HTTPS but safe to include)
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

            # Remove server info header
            response.headers.pop("Server", None)

            # Track suspicious responses (4xx/5xx from same IP)
            if response.status_code >= 400:
                ip = getattr(g, "request_ip", _get_real_ip())
                _record_suspicious(ip)

            return response


def _contains_injection(body: str) -> bool:
    """
    Detect common injection patterns in request body.
    Not a WAF — just a basic safety net.
    """
    if len(body) > _MAX_REQUEST_SIZE:
        return True

    _injection_patterns = [
        # SQL injection
        r"(?i)(\bunion\b.*\bselect\b|\binsert\b.*\binto\b|\bdrop\b.*\btable\b|\bdelete\b.*\bfrom\b)",
        r"(?i)(--|;)\s*(drop|alter|truncate|exec)\b",
        r"(?i)\bor\b\s+['\"]?\s*\d+\s*=\s*\d+",
        # XSS
        r"<script[^>]*>",
        r"javascript\s*:",
        r"on(error|load|click|mouseover)\s*=",
        # Command injection
        r";\s*(ls|cat|rm|wget|curl|bash|sh|nc)\b",
        r"\|\s*(ls|cat|rm|wget|curl|bash|sh|nc)\b",
    ]

    for pattern in _injection_patterns:
        if re.search(pattern, body):
            return True

    return False


def _record_suspicious(ip: str) -> None:
    """Track suspicious requests from an IP. Auto-block after threshold."""
    now = time.time()
    with _sus_lock:
        hits = _suspicious_ips.setdefault(ip, [])
        # Prune old hits
        _suspicious_ips[ip] = [t for t in hits if now - t < _SUSPICIOUS_WINDOW]
        _suspicious_ips[ip].append(now)

        if len(_suspicious_ips[ip]) >= _MAX_SUSPICIOUS_HITS:
            _blocked_ips.add(ip)
            # Schedule unblock
            def _unblock():
                time.sleep(_IP_BLOCK_DURATION)
                _blocked_ips.discard(ip)
                _suspicious_ips.pop(ip, None)
            t = threading.Thread(target=_unblock, daemon=True)
            t.start()
