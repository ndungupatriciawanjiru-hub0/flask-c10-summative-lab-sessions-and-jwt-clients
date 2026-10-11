from flask import Flask
from flask_restful import Api

from config import Config
from extensions import bcrypt, db, migrate
from resources.auth import CheckSession, Login, Logout, Signup
from resources.notes import NoteDetail, NoteList


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # A new Api per app keeps create_app() safe to call more than once (tests).
    api = Api(app)
    api.add_resource(Signup, "/signup")
    api.add_resource(Login, "/login")
    api.add_resource(CheckSession, "/check_session")
    api.add_resource(Logout, "/logout")
    api.add_resource(NoteList, "/notes")
    api.add_resource(NoteDetail, "/notes/<int:note_id>")

    return app


app = create_app()

if __name__ == "__main__":
    # Port 5555 matches the proxy in the provided React clients.
    app.run(port=5555, debug=True)
