from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from decorators import login_required
from extensions import db
from models import Note
from schemas import NoteSchema, flatten_errors

DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 50


def get_own_note(note_id, user):
    """Fetch a note only if it belongs to the user. Other users' notes look
    identical to missing ones so their existence is not revealed."""
    return Note.query.filter_by(id=note_id, user_id=user.id).first()


class NoteList(Resource):
    @login_required
    def get(self, user):
        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", DEFAULT_PER_PAGE))
        except ValueError:
            return {"errors": ["page and per_page must be integers."]}, 400
        if page < 1 or per_page < 1:
            return {"errors": ["page and per_page must be at least 1."]}, 400

        pagination = (
            Note.query.filter_by(user_id=user.id)
            .order_by(Note.created_at.desc(), Note.id.desc())
            .paginate(
                page=page,
                per_page=min(per_page, MAX_PER_PAGE),
                error_out=False,
            )
        )
        return {
            "items": [note.to_dict() for note in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }, 200

    @login_required
    def post(self, user):
        try:
            data = NoteSchema().load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"errors": flatten_errors(err)}, 422

        note = Note(user_id=user.id, **data)
        db.session.add(note)
        db.session.commit()
        return note.to_dict(), 201


class NoteDetail(Resource):
    @login_required
    def get(self, note_id, user):
        note = get_own_note(note_id, user)
        if note is None:
            return {"errors": ["Note not found."]}, 404
        return note.to_dict(), 200

    @login_required
    def patch(self, note_id, user):
        note = get_own_note(note_id, user)
        if note is None:
            return {"errors": ["Note not found."]}, 404

        try:
            data = NoteSchema().load(
                request.get_json(silent=True) or {}, partial=True
            )
        except ValidationError as err:
            return {"errors": flatten_errors(err)}, 422

        for field, value in data.items():
            setattr(note, field, value)
        db.session.commit()
        return note.to_dict(), 200

    @login_required
    def delete(self, note_id, user):
        note = get_own_note(note_id, user)
        if note is None:
            return {"errors": ["Note not found."]}, 404
        db.session.delete(note)
        db.session.commit()
        return "", 204
