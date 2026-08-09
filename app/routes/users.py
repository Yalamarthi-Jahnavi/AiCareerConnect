"""
User Profile Routes
====================
Handles user profile viewing and updating.

WHY THIS FILE EXISTS:
    User profile management is separate from auth because auth deals
    with identity verification while this deals with profile data.
    
Endpoints:
    GET  /api/users/profile       - Get current user profile
    PUT  /api/users/profile       - Update current user profile
    GET  /api/users/<id>          - Get any user's public profile
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get the current user's full profile."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    return jsonify({'success': True, 'user': user.to_dict()}), 200


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update the current user's profile information."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    updatable_fields = ['full_name', 'phone', 'location', 'bio', 'skills', 'experience_years']
    for field in updatable_fields:
        if field in data:
            if field == 'skills' and isinstance(data[field], list):
                setattr(user, field, ','.join(data[field]))
            else:
                setattr(user, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully',
        'user': user.to_dict(),
    }), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_public(user_id):
    """Get a user's public profile (limited info)."""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Return limited public info
    public_data = {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'location': user.location,
        'bio': user.bio,
        'skills': user.skills.split(',') if user.skills else [],
        'experience_years': user.experience_years,
    }
    
    return jsonify({'success': True, 'user': public_data}), 200
