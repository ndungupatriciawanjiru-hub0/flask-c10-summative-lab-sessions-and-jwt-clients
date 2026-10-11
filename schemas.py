"""Marshmallow schemas that validate incoming JSON."""
from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate


class NoteSchema(Schema):
    class Meta:
        # Ignore unknown keys so clients cannot set fields like user_id.
        unknown = EXCLUDE

    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    content = fields.String(required=True, validate=validate.Length(min=1))
    category = fields.String(
        allow_none=True, validate=validate.Length(max=50)
    )


def flatten_errors(err: ValidationError):
    """Turn marshmallow's {field: [msgs]} into the flat list the client shows."""
    return [f"{field}: {msg}" for field, msgs in err.messages.items() for msg in msgs]
