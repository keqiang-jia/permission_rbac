from functools import wraps
from flask import abort, session, g
from models import User


# 登录验证装饰器
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('_user_id', 0)
        user = User.query.get(int(user_id))
        if not user:
            return {'status': 'fail', 'message': '请先登录之后再进行操作'}
        g.user = user
        result = func(*args, **kwargs)
        return result

    return wrapper


# 权限验证装饰器
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print('permission', permission, session.get('permission', ''))
            if permission not in session.get('permission', ''):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# 角色验证装饰器
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            role_code = [_role.code for _role in g.user.role]
            print('role', role, role_code)
            if role not in role_code:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# 管理员验证装饰器
def admin_required(f):
    return role_required('level3')(f)
