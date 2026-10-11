from datetime import datetime

from sqlalchemy.orm import validates

from extensions import bcrypt, db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)

    notes = db.relationship(
        "Note", back_populates="user", cascade="all, delete-orphan"
    )

    @validates("username")
    def validate_username(self, key, value):
        value = (value or "").strip()
        if not value:
            raise ValueError("Username is required.")
        if len(value) > 50:
            raise ValueError("Username must be 50 characters or fewer.")
        return value

    @property
    def password_hash(self):
        # Hashes are never readable, so they cannot leak into a response.
        raise AttributeError("Password hashes are not readable.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(
            password.encode("utf-8")
        ).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode("utf-8")
        )

    def to_dict(self):
        return {"id": self.id, "username": self.username}


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="notes")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id,
        }
