"""Reset the database and fill it with starter users and notes.

Run with: python seed.py
"""
from faker import Faker

from app import app
from extensions import db
from models import Note, User

fake = Faker()

# Demo accounts you can log in with (password is "password123" for both).
DEMO_USERS = ["alice", "bob"]
NOTES_PER_USER = 12  # more than one page at the default page size of 10
CATEGORIES = ["work", "personal", "ideas", "study"]


def seed():
    with app.app_context():
        # Delete notes first so the foreign key to users is never violated.
        Note.query.delete()
        User.query.delete()

        for username in DEMO_USERS:
            user = User(username=username)
            user.password_hash = "password123"
            db.session.add(user)
            db.session.flush()  # assigns user.id before the notes are created

            for _ in range(NOTES_PER_USER):
                db.session.add(
                    Note(
                        title=fake.sentence(nb_words=4).rstrip("."),
                        content=fake.paragraph(nb_sentences=3),
                        category=fake.random_element(CATEGORIES),
                        user_id=user.id,
                    )
                )

        db.session.commit()
        print(
            f"Seeded {User.query.count()} users and {Note.query.count()} notes."
        )


if __name__ == "__main__":
    seed()
