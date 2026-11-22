from app.models import User, Note, db

def test_user_password_hashing(app):
    with app.app_context():
        user = User(username="alice", email="alice@example.com")
        user.set_password("secretpass")
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "secretpass"
        assert user.check_password("secretpass") is True
        assert user.check_password("wrongpass") is False

def test_user_to_dict(app):
    with app.app_context():
        user = User(username="bob", email="bob@example.com")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

        d = user.to_dict()
        assert d["username"] == "bob"
        assert d["email"] == "bob@example.com"
        assert d["notes_count"] == 0

def test_note_creation_and_relationship(app, test_user):
    with app.app_context():
        note = Note(
            user_id=test_user,
            title="Kubernetes Guide",
            content="Deploy pods and services",
            category="DevOps",
            is_pinned=True
        )
        db.session.add(note)
        db.session.commit()

        assert note.id is not None
        assert note.title == "Kubernetes Guide"
        assert note.is_pinned is True
        assert note.author.username == "testuser"

        d = note.to_dict()
        assert d["title"] == "Kubernetes Guide"
        assert d["category"] == "DevOps"
        assert d["is_pinned"] is True
