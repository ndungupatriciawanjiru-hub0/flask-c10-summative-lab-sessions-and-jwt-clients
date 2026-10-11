from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from decorators import current_user
from extensions import db
from models import User

MIN_PASSWORD_LENGTH = 6


class Signup(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        confirmation = data.get("password_confirmation")

        errors = []
        if not username:
            errors.append("Username is required.")
        elif User.query.filter_by(username=username).first():
            errors.append("Username is already taken.")
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
            )
        if confirmation is not None and confirmation != password:
            errors.append("Password confirmation does not match.")
        if errors:
            return {"errors": errors}, 422

        try:
            user = User(username=username)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
        except ValueError as exc:
            db.session.rollback()
            return {"errors": [str(exc)]}, 422
        except IntegrityError:
            # Covers a race where the username was taken after the check above.
            db.session.rollback()
            return {"errors": ["Username is already taken."]}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201


class Login(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        user = User.query.filter_by(username=username).first()
        if user is None or not user.authenticate(password):
            return {"errors": ["Invalid username or password."]}, 401

        session["user_id"] = user.id
        return user.to_dict(), 200


class CheckSession(Resource):
    def get(self):
        user = current_user()
        if user is None:
            # The client only treats 2xx as logged in, so this must not be 200.
            return {}, 401
        return user.to_dict(), 200


class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return "", 204
