"""
Helper Utilities
==================
Miscellaneous helper functions used across the application.

WHY THIS FILE EXISTS:
    Small, reusable functions that don't belong in any specific service.
    Things like formatting responses, pagination helpers, and date utils.
"""

from flask import jsonify


def api_response(success=True, message='', data=None, status_code=200):
    """
    Create a standardized API response.
    
    Ensures every API response has the same structure:
    { "success": bool, "message": str, "data": any }
    """
    response = {
        'success': success,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code


def paginate_query(query, page=1, per_page=10):
    """
    Helper to paginate a SQLAlchemy query and return formatted results.
    
    Returns:
        dict: Contains items, total, pages, current_page
    """
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
    }


def skills_string_to_list(skills_string):
    """Convert comma-separated skills string to a cleaned list."""
    if not skills_string:
        return []
    return [s.strip().lower() for s in skills_string.split(',') if s.strip()]


def skills_list_to_string(skills_list):
    """Convert a list of skills to a comma-separated string."""
    if not skills_list:
        return ''
    return ','.join([s.strip() for s in skills_list if s.strip()])
