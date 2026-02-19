"""
PATH: api/middleware/auth.py
PURPOSE: JWT-based authentication middleware

FLOW:
 ┌─────────┐    ┌──────────┐    ┌────────────┐    ┌─────────┐
 │ Request │───▶│ Extract  │───▶│ Validate   │───▶│ Set     │
 │         │    │   JWT    │    │   Token    │    │ User    │
 └─────────┘    └──────────┘    └────────────┘    └─────────┘

Features:
- JWT token authentication
- User registration/login
- Role-based access control
- Token refresh
- Rate limiting support
"""

import os
import hashlib
import hmac
import json
import secrets as _secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple
import base64

from flask import request, jsonify, g, current_app


# Configuration — JWT_SECRET is resolved from env vars with a secure random fallback.
# In production set JWT_SECRET (or SECRET_KEY) explicitly so tokens survive server restarts.
_jwt_secret = (
    os.environ.get("JWT_SECRET")
    or os.environ.get("SECRET_KEY")
    or _secrets.token_hex(32)
)

AUTH_CONFIG = {
    "jwt_secret": _jwt_secret,
    "jwt_algorithm": "HS256",
    "access_token_expiry": 3600,  # 1 hour
    "refresh_token_expiry": 86400 * 7,  # 7 days
    "password_min_length": 8,
    # ── Account lockout ──
    "max_failed_attempts": 5,          # lock after N failures
    "lockout_duration": 900,           # 15 minutes
    "failed_attempt_window": 600,      # track failures within 10 min
}

# ── Failed login attempt tracker (IP + email) ──────────────────
# Key: "ip:<addr>" or "email:<addr>" → list of timestamps
_failed_attempts: Dict[str, list] = {}
_failed_lock = __import__("threading").Lock()


def _record_failed_attempt(ip: str, email: str) -> None:
    """Record a failed login attempt for both IP and email."""
    now = time.time()
    window = AUTH_CONFIG["failed_attempt_window"]
    with _failed_lock:
        for key in (f"ip:{ip}", f"email:{email}"):
            attempts = _failed_attempts.setdefault(key, [])
            # Prune old entries
            _failed_attempts[key] = [t for t in attempts if now - t < window]
            _failed_attempts[key].append(now)


def _is_locked_out(ip: str, email: str) -> Tuple[bool, int]:
    """
    Check if the IP or email is locked out.
    Returns (is_locked, seconds_remaining).
    """
    now = time.time()
    max_attempts = AUTH_CONFIG["max_failed_attempts"]
    lockout_dur = AUTH_CONFIG["lockout_duration"]
    window = AUTH_CONFIG["failed_attempt_window"]

    with _failed_lock:
        for key in (f"ip:{ip}", f"email:{email}"):
            attempts = _failed_attempts.get(key, [])
            recent = [t for t in attempts if now - t < window]
            if len(recent) >= max_attempts:
                last = max(recent)
                remaining = int(lockout_dur - (now - last))
                if remaining > 0:
                    return True, remaining
    return False, 0


def _clear_failed_attempts(ip: str, email: str) -> None:
    """Clear failed attempt counters on successful login."""
    with _failed_lock:
        _failed_attempts.pop(f"ip:{ip}", None)
        _failed_attempts.pop(f"email:{email}", None)

# ── Persistent user store (JSON file) ───────────────────────────
_USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "users.json")


def _load_users() -> Dict[str, Dict[str, Any]]:
    """Load users from JSON file on disk."""
    try:
        if os.path.exists(_USERS_FILE):
            with open(_USERS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_users() -> None:
    """Persist users dict to JSON file."""
    try:
        os.makedirs(os.path.dirname(_USERS_FILE), exist_ok=True)
        with open(_USERS_FILE, "w") as f:
            json.dump(USERS, f, indent=2, default=str)
    except Exception as exc:
        print(f"[auth] Warning: could not save users file: {exc}")


USERS: Dict[str, Dict[str, Any]] = _load_users()

# Active sessions (token -> user_id)
SESSIONS: Dict[str, str] = {}


def _base64_url_encode(data: bytes) -> str:
    """URL-safe base64 encoding without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64_url_decode(data: str) -> bytes:
    """URL-safe base64 decoding."""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)


def _create_jwt(payload: Dict[str, Any], secret: str = None, expires_in: int = None) -> str:
    """
    Create a JWT token.
    
    Simple implementation - for production use PyJWT or similar.
    """
    secret = secret or AUTH_CONFIG["jwt_secret"]
    expires_in = expires_in or AUTH_CONFIG["access_token_expiry"]
    
    # Header
    header = {"alg": "HS256", "typ": "JWT"}
    
    # Payload with expiration
    now = int(time.time())
    payload = {
        **payload,
        "iat": now,
        "exp": now + expires_in,
    }
    
    # Encode
    header_b64 = _base64_url_encode(json.dumps(header).encode())
    payload_b64 = _base64_url_encode(json.dumps(payload).encode())
    
    # Sign
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = _base64_url_encode(signature)
    
    return f"{message}.{signature_b64}"


def _verify_jwt(token: str, secret: str = None) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Returns payload if valid, None if invalid.
    """
    secret = secret or AUTH_CONFIG["jwt_secret"]
    
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        message = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        actual_sig = _base64_url_decode(signature_b64)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        # Decode payload
        payload = json.loads(_base64_url_decode(payload_b64))
        
        # Check expiration
        if payload.get("exp", 0) < int(time.time()):
            return None
        
        return payload
        
    except Exception:
        return None


def _hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """Hash a password with salt."""
    if salt is None:
        salt = os.urandom(32).hex()
    
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        100000
    ).hex()
    
    return hashed, salt


def _verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against hash."""
    test_hash, _ = _hash_password(password, salt)
    return hmac.compare_digest(test_hash, hashed)


def _validate_email(email: str) -> bool:
    """Basic but strict email validation."""
    import re
    if not email or len(email) > 254:
        return False
    pattern = r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$'
    return bool(re.match(pattern, email))


# Disposable / temporary email domains — block throwaway signups
_DISPOSABLE_DOMAINS = frozenset({
    "mailinator.com", "guerrillamail.com", "guerrillamail.net", "tempmail.com",
    "throwaway.email", "10minutemail.com", "trashmail.com", "yopmail.com",
    "sharklasers.com", "guerrillamailblock.com", "grr.la", "dispostable.com",
    "mailnesia.com", "maildrop.cc", "discard.email", "getnada.com",
    "tempail.com", "temp-mail.org", "fakeinbox.com", "mailcatch.com",
    "meltmail.com", "harakirimail.com", "tmail.ws", "mohmal.com",
    "burnermail.io", "inboxkitten.com", "mailsac.com", "tempmailo.com",
    "emailondeck.com", "crazymailing.com", "mytemp.email",
    "minutemail.com", "tempmailaddress.com", "emailfake.com",
    "generator.email", "safetymail.info", "trashmail.me", "trashmail.net",
})


def _is_disposable_email(email: str) -> bool:
    """Check if email uses a known disposable/temporary domain."""
    domain = email.rsplit("@", 1)[-1].lower()
    return domain in _DISPOSABLE_DOMAINS


# ── Registration rate tracking (per IP) ──────────────────────
_registration_tracker: Dict[str, list] = {}
_reg_lock = __import__("threading").Lock()
_MAX_REGISTRATIONS_PER_IP = int(os.environ.get("MAX_REGISTRATIONS_PER_IP", "3"))
_REGISTRATION_WINDOW = int(os.environ.get("REGISTRATION_WINDOW", "3600"))  # 1 hour


def _check_registration_rate(ip: str) -> Tuple[bool, str]:
    """Limit registrations per IP to prevent mass account creation."""
    now = time.time()
    with _reg_lock:
        regs = _registration_tracker.get(ip, [])
        recent = [t for t in regs if now - t < _REGISTRATION_WINDOW]
        _registration_tracker[ip] = recent

        if len(recent) >= _MAX_REGISTRATIONS_PER_IP:
            return False, f"Too many registrations from this IP. Try again in {_REGISTRATION_WINDOW // 60} minutes."
        return True, ""


def _record_registration(ip: str) -> None:
    """Record a successful registration from this IP."""
    with _reg_lock:
        _registration_tracker.setdefault(ip, []).append(time.time())


def _validate_password_strength(password: str) -> Optional[str]:
    """
    Enforce password complexity.
    Returns error message or None if valid.
    """
    min_len = AUTH_CONFIG["password_min_length"]
    if len(password) < min_len:
        return f"Password must be at least {min_len} characters"
    if len(password) > 128:
        return "Password must be 128 characters or fewer"
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number"
    # Check for common weak passwords
    weak = {"password", "12345678", "qwerty123", "letmein", "welcome1", "admin123", "changeme"}
    if password.lower().strip() in weak:
        return "Password is too common — choose something stronger"
    return None


def _sanitize_text(text: str, max_length: int = 100) -> str:
    """Strip dangerous characters and limit length."""
    import re
    # Remove any HTML / script tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove null bytes
    text = text.replace('\x00', '')
    # Limit length
    return text[:max_length].strip()


def register_user(
    email: str,
    password: str,
    name: str = "",
    role: str = "user",
    client_ip: str = "unknown",
) -> Tuple[bool, str, Optional[Dict]]:
    """
    Register a new user.
    
    Returns (success, message, user_data).
    """
    # ── Input sanitization ──
    email = email.strip().lower()
    name = _sanitize_text(name, 100)

    # ── Email validation ──
    if not _validate_email(email):
        return False, "Invalid email address", None

    # ── Block disposable emails ──
    if _is_disposable_email(email):
        return False, "Temporary/disposable email addresses are not allowed. Please use a real email.", None

    # ── Registration rate limit per IP ──
    allowed, rate_msg = _check_registration_rate(client_ip)
    if not allowed:
        return False, rate_msg, None

    # ── Password strength ──
    pw_error = _validate_password_strength(password)
    if pw_error:
        return False, pw_error, None
    
    if email in USERS:
        return False, "Email already registered", None
    
    # Hash password
    password_hash, salt = _hash_password(password)
    
    # Create user with usage tracking
    user_id = hashlib.sha256(email.lower().encode()).hexdigest()[:16]
    user = {
        "id": user_id,
        "email": email.lower(),
        "name": name or email.split('@')[0],
        "password_hash": password_hash,
        "salt": salt,
        "role": role,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "is_active": True,
        "registered_ip": client_ip,
    }

    _record_registration(client_ip)
    
    USERS[email.lower()] = user
    _save_users()
    
    # Return safe user data
    safe_user = {k: v for k, v in user.items() if k not in ('password_hash', 'salt')}
    return True, "User registered successfully", safe_user


def login_user(email: str, password: str, client_ip: str = "unknown") -> Tuple[bool, str, Optional[Dict]]:
    """
    Authenticate a user and return tokens.
    Includes account lockout after repeated failures.
    
    Returns (success, message, token_data).
    """
    email = email.lower().strip()

    # ── Check lockout before even touching the DB ──
    locked, remaining = _is_locked_out(client_ip, email)
    if locked:
        return False, f"Account temporarily locked. Try again in {remaining // 60 + 1} minutes.", None

    if email not in USERS:
        _record_failed_attempt(client_ip, email)
        return False, "Invalid credentials", None
    
    user = USERS[email]
    
    if not user.get("is_active", True):
        return False, "Account is disabled. Contact support.", None
    
    if not _verify_password(password, user["password_hash"], user["salt"]):
        _record_failed_attempt(client_ip, email)
        # Check if this attempt triggers lockout — give helpful message
        locked_now, secs = _is_locked_out(client_ip, email)
        if locked_now:
            return False, f"Too many failed attempts. Account locked for {secs // 60 + 1} minutes.", None
        return False, "Invalid credentials", None
    
    # ── Success — clear failed attempts ──
    _clear_failed_attempts(client_ip, email)
    
    # Update last login
    user["last_login"] = datetime.now().isoformat()
    _save_users()
    
    # Create tokens
    access_token = _create_jwt(
        {"sub": user["id"], "email": email, "role": user["role"]},
        expires_in=AUTH_CONFIG["access_token_expiry"]
    )
    
    refresh_token = _create_jwt(
        {"sub": user["id"], "type": "refresh"},
        expires_in=AUTH_CONFIG["refresh_token_expiry"]
    )
    
    # Store session
    SESSIONS[access_token[:32]] = user["id"]
    
    return True, "Login successful", {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": AUTH_CONFIG["access_token_expiry"],
        "user": {k: v for k, v in user.items() if k not in ('password_hash', 'salt')}
    }


def refresh_access_token(refresh_token: str) -> Tuple[bool, str, Optional[str]]:
    """
    Refresh an access token.
    
    Returns (success, message, new_access_token).
    """
    payload = _verify_jwt(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        return False, "Invalid refresh token", None
    
    user_id = payload.get("sub")
    
    # Find user
    user = None
    for u in USERS.values():
        if u["id"] == user_id:
            user = u
            break
    
    if not user:
        return False, "User not found", None
    
    # Create new access token
    access_token = _create_jwt(
        {"sub": user["id"], "email": user["email"], "role": user["role"]},
        expires_in=AUTH_CONFIG["access_token_expiry"]
    )
    
    return True, "Token refreshed", access_token


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current authenticated user from request context."""
    return getattr(g, 'current_user', None)


def require_auth(f):
    """
    Decorator to require authentication.
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            user = get_current_user()
            return jsonify(user)
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Missing or invalid authorization header'
            }), 401
        
        token = auth_header[7:]  # Remove 'Bearer '
        payload = _verify_jwt(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        # Find user
        user_id = payload.get('sub')
        user = None
        for u in USERS.values():
            if u['id'] == user_id:
                user = {k: v for k, v in u.items() if k not in ('password_hash', 'salt')}
                break
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 401
        
        # Store in request context
        g.current_user = user
        g.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated


def require_role(roles: List[str]):
    """
    Decorator to require specific role(s).
    
    Usage:
        @app.route('/admin')
        @require_auth
        @require_role(['admin'])
        def admin_route():
            return jsonify({'message': 'Admin only'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required'
                }), 401
            
            if user.get('role') not in roles:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions'
                }), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator


def optional_auth(f):
    """
    Decorator for optional authentication.
    
    Sets current_user if token provided, but doesn't require it.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            payload = _verify_jwt(token)
            
            if payload:
                user_id = payload.get('sub')
                for u in USERS.values():
                    if u['id'] == user_id:
                        g.current_user = {k: v for k, v in u.items() if k not in ('password_hash', 'salt')}
                        g.token_payload = payload
                        break
        
        return f(*args, **kwargs)
    
    return decorated
