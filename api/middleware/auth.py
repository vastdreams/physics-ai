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
}

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


def register_user(
    email: str,
    password: str,
    name: str = "",
    role: str = "user"
) -> Tuple[bool, str, Optional[Dict]]:
    """
    Register a new user.
    
    Returns (success, message, user_data).
    """
    # Validation
    if not email or '@' not in email:
        return False, "Invalid email address", None
    
    if len(password) < AUTH_CONFIG["password_min_length"]:
        return False, f"Password must be at least {AUTH_CONFIG['password_min_length']} characters", None
    
    if email.lower() in USERS:
        return False, "Email already registered", None
    
    # Hash password
    password_hash, salt = _hash_password(password)
    
    # Create user
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
    }
    
    USERS[email.lower()] = user
    _save_users()
    
    # Return safe user data
    safe_user = {k: v for k, v in user.items() if k not in ('password_hash', 'salt')}
    return True, "User registered successfully", safe_user


def login_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Authenticate a user and return tokens.
    
    Returns (success, message, token_data).
    """
    email = email.lower()
    
    if email not in USERS:
        return False, "Invalid credentials", None
    
    user = USERS[email]
    
    if not user.get("is_active", True):
        return False, "Account is disabled", None
    
    if not _verify_password(password, user["password_hash"], user["salt"]):
        return False, "Invalid credentials", None
    
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
