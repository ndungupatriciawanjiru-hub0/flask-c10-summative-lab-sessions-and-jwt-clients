# Notes API: Full Auth Flask Backend

A Flask REST API for a personal productivity app. Users sign up, log in with session-based authentication, and manage their own notes. Passwords are hashed with Flask-Bcrypt, every notes route requires login, and users can only see or change their own notes. The notes list is paginated.

Built for the Moringa summative lab "Full Auth Flask Backend: Productivity App". It works with the provided `client-with-sessions` React app (the dev server runs on port 5555 to match its proxy).

## Tech stack

Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Migrate, Flask-Bcrypt, Marshmallow, Faker, pytest, SQLite.

## Project structure

- `app.py`: app factory, route registration, entry point
- `config.py`: configuration (secret key, database URI)
- `extensions.py`: db, migrate and bcrypt instances
- `models.py`: `User` and `Note` models
- `schemas.py`: Marshmallow validation for notes
- `decorators.py`: `login_required` and current-user lookup
- `resources/auth.py`: signup, login, check_session, logout
- `resources/notes.py`: notes CRUD with pagination
- `seed.py`: starter data
- `tests/`: pytest suite

## Installation

1. Install dependencies: `pipenv install`
2. Open the environment: `pipenv shell`
3. Set the app for the Flask CLI: `export FLASK_APP=app.py`
4. Apply the database migrations: `flask db upgrade`
5. Seed the database: `python seed.py`

Seeding creates two users, `alice` and `bob` (password `password123` for both), each with 12 notes. Running it again resets the data.

Optional: set a `SECRET_KEY` environment variable to sign session cookies with your own key.

## Running

Start the server with `python app.py` (port 5555) or `flask run -p 5555`.

To use the provided frontend, run `npm install` and `npm start` inside `client-with-sessions`.

## Running the tests

Run `pytest` from the project root.

## Endpoints

All responses are JSON. Errors look like `{"errors": ["message"]}`. Authentication uses a session cookie set by signup or login.

### Auth

- `POST /signup`: create an account and log in. Body: `username`, `password` (6+ characters), `password_confirmation`. Returns 201 with `{id, username}`, or 422 for validation errors such as a taken username or mismatched confirmation.
- `POST /login`: log in. Body: `username`, `password`. Returns 200 with `{id, username}`, or 401 for invalid credentials.
- `GET /check_session`: returns 200 with `{id, username}` if logged in, otherwise 401 with `{}`.
- `DELETE /logout`: ends the session. Returns 204.

### Notes (login required, 401 otherwise)

- `GET /notes`: list your notes, newest first, paginated. Query params: `page` (default 1), `per_page` (default 10, max 50). Returns 200 with `items`, `page`, `per_page`, `total`, `pages`, `has_next`, `has_prev`. Invalid paging values return 400.
- `POST /notes`: create a note. Body: `title` (required, up to 120 characters), `content` (required), `category` (optional). Returns 201 with the note, or 422 for validation errors.
- `GET /notes/<id>`: fetch one of your notes. Returns 200, or 404.
- `PATCH /notes/<id>`: update `title`, `content` and/or `category`. Returns 200 with the updated note, 404, or 422.
- `DELETE /notes/<id>`: delete a note. Returns 204, or 404.

A note that belongs to another user returns 404, the same as a note that does not exist.

### Note fields

`id`, `title`, `content`, `category`, `created_at`, `updated_at`, `user_id`
