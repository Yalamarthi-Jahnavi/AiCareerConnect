"""
Custom Decorators
==================
Reusable decorators for route protection and access control.

WHY THIS FILE EXISTS:
    Instead of repeating role-check logic in every route, decorators
    let you write @role_required('employer') once. DRY principle.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User


def role_required(*roles):
    """
    Decorator to restrict route access to specific user roles.
    
    Usage:
        @role_required('employer', 'admin')
        def create_job():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            if user.role not in roles:
                return jsonify({
                    'success': False,
                    'message': f'Access denied. Required role: {", ".join(roles)}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def active_user_required(f):
    """
    Decorator to ensure the user account is active.
    
    Usage:
        @active_user_required
        def some_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Account is deactivated'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function
