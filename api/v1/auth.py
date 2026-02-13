"""
PATH: api/v1/auth.py
PURPOSE: Authentication REST API endpoints

ENDPOINTS:
- POST /auth/register    - Register new user
- POST /auth/login       - Login and get tokens
- POST /auth/refresh     - Refresh access token
- GET  /auth/me          - Get current user
- PUT  /auth/me          - Update current user
- POST /auth/logout      - Logout (invalidate session)
- POST /auth/change-password - Change password
"""

from flask import Blueprint, jsonify, request

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.middleware.auth import (
    register_user,
    login_user,
    refresh_access_token,
    require_auth,
    require_role,
    get_current_user,
    USERS,
    _hash_password,
    _verify_password,
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json() or {}
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    
    if not email or not password:
        return jsonify({
            'success': False,
            'error': 'Email and password are required'
        }), 400
    
    success, message, user = register_user(
        email=email,
        password=password,
        name=name,
        role='user'  # Default role
    )
    
    if not success:
        return jsonify({
            'success': False,
            'error': message
        }), 400
    
    return jsonify({
        'success': True,
        'message': message,
        'user': user
    })


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and get access/refresh tokens."""
    data = request.get_json() or {}
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({
            'success': False,
            'error': 'Email and password are required'
        }), 400
    
    success, message, token_data = login_user(email, password)
    
    if not success:
        return jsonify({
            'success': False,
            'error': message
        }), 401
    
    return jsonify({
        'success': True,
        'message': message,
        **token_data
    })


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token."""
    data = request.get_json() or {}
    
    refresh_token = data.get('refresh_token', '')
    
    if not refresh_token:
        return jsonify({
            'success': False,
            'error': 'Refresh token is required'
        }), 400
    
    success, message, access_token = refresh_access_token(refresh_token)
    
    if not success:
        return jsonify({
            'success': False,
            'error': message
        }), 401
    
    return jsonify({
        'success': True,
        'message': message,
        'access_token': access_token,
        'token_type': 'Bearer'
    })


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_me():
    """Get current authenticated user."""
    user = get_current_user()
    
    return jsonify({
        'success': True,
        'user': user
    })


@auth_bp.route('/me', methods=['PUT'])
@require_auth
def update_me():
    """Update current user profile."""
    user = get_current_user()
    data = request.get_json() or {}
    
    # Find and update user
    email = user['email']
    if email in USERS:
        if 'name' in data:
            USERS[email]['name'] = data['name'].strip()
        
        # Return updated user
        updated = {k: v for k, v in USERS[email].items() if k not in ('password_hash', 'salt')}
        
        return jsonify({
            'success': True,
            'message': 'Profile updated',
            'user': updated
        })
    
    return jsonify({
        'success': False,
        'error': 'User not found'
    }), 404


@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change current user's password."""
    user = get_current_user()
    data = request.get_json() or {}
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({
            'success': False,
            'error': 'Current and new passwords are required'
        }), 400
    
    if len(new_password) < 8:
        return jsonify({
            'success': False,
            'error': 'New password must be at least 8 characters'
        }), 400
    
    email = user['email']
    if email in USERS:
        stored_user = USERS[email]
        
        # Verify current password
        if not _verify_password(current_password, stored_user['password_hash'], stored_user['salt']):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 401
        
        # Update password
        new_hash, new_salt = _hash_password(new_password)
        USERS[email]['password_hash'] = new_hash
        USERS[email]['salt'] = new_salt
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
    
    return jsonify({
        'success': False,
        'error': 'User not found'
    }), 404


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout current user (client should discard tokens)."""
    # In a full implementation, we would invalidate the token server-side
    # For now, just return success (client discards token)
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


# Admin endpoints

@auth_bp.route('/users', methods=['GET'])
@require_auth
@require_role(['admin'])
def list_users():
    """List all users (admin only)."""
    users = [
        {k: v for k, v in u.items() if k not in ('password_hash', 'salt')}
        for u in USERS.values()
    ]
    
    return jsonify({
        'success': True,
        'count': len(users),
        'users': users
    })


@auth_bp.route('/users/<user_id>/role', methods=['PUT'])
@require_auth
@require_role(['admin'])
def update_user_role(user_id):
    """Update a user's role (admin only)."""
    data = request.get_json() or {}
    new_role = data.get('role', '')
    
    valid_roles = ['user', 'researcher', 'admin']
    if new_role not in valid_roles:
        return jsonify({
            'success': False,
            'error': f'Invalid role. Must be one of: {valid_roles}'
        }), 400
    
    # Find user
    for email, user in USERS.items():
        if user['id'] == user_id:
            USERS[email]['role'] = new_role
            
            return jsonify({
                'success': True,
                'message': f'Role updated to {new_role}',
                'user': {k: v for k, v in USERS[email].items() if k not in ('password_hash', 'salt')}
            })
    
    return jsonify({
        'success': False,
        'error': 'User not found'
    }), 404


@auth_bp.route('/users/<user_id>/disable', methods=['POST'])
@require_auth
@require_role(['admin'])
def disable_user(user_id):
    """Disable a user account (admin only)."""
    # Prevent self-disable
    current_user = get_current_user()
    if current_user['id'] == user_id:
        return jsonify({
            'success': False,
            'error': 'Cannot disable your own account'
        }), 400
    
    for email, user in USERS.items():
        if user['id'] == user_id:
            USERS[email]['is_active'] = False
            
            return jsonify({
                'success': True,
                'message': 'User disabled'
            })
    
    return jsonify({
        'success': False,
        'error': 'User not found'
    }), 404


# Create default admin user on module load
# SECURITY: Set ADMIN_EMAIL and ADMIN_PASSWORD in .env for production.
# The default password is only suitable for local development.
_DEFAULT_ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@beyondfrontier.local')
_DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', os.getenv('SECRET_KEY', 'change-me-in-production'))

if _DEFAULT_ADMIN_EMAIL not in USERS:
    register_user(
        email=_DEFAULT_ADMIN_EMAIL,
        password=_DEFAULT_ADMIN_PASSWORD,
        name='Administrator',
        role='admin'
    )
