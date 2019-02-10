from functools import wraps
from flask import g, request, redirect, url_for
from .persistence import UserDAO
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.view_decorators import verify_jwt_in_request

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = UserDAO.get_by_id(get_jwt_identity())
        if not current_user.admin:
            return  {
                        "msg": "you are not admin"
                    }, 403
        return f(*args, **kwargs)
    return decorated_function



def jwt_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except:
            return  {
                        "msg": "JWT not valid"
                    }, 403
        return f(*args, **kwargs)
    return decorated_function
