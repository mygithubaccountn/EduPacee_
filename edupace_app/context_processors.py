from .utils import get_user_role


def user_role_context(request):
    """Add user role information to template context"""
    if request.user.is_authenticated:
        role = get_user_role(request.user)
        role_display_map = {
            'student': 'Student',
            'teacher': 'Teacher',
            'academic_board': 'Department Head',
        }
        role_display = role_display_map.get(role, 'User')
        return {
            'user_role': role,
            'user_role_display': role_display,
        }
    return {
        'user_role': None,
        'user_role_display': None,
    }

