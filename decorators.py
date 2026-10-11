from functools import wraps

from flask import session

from extensions import db
from models import User


def current_user():
    """Return the logged-in User, or None if the session is empty or stale."""
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def login_required(func):
    """Reject the request with 401 unless a valid user is in the session."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            session.pop("user_id", None)
            return {"errors": ["Unauthorized. Please log in."]}, 401
        return func(*args, user=user, **kwargs)

    return wrapper
