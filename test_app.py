
import pytest
import sqlite3
from app import create_app


@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / "test_polls.db"

    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "DATABASE": str(db_path)
    })

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def create_test_poll(client):
    response = client.post("/create", data={
        "question": "Which is your favourite app?",
        "options": ["Instagram", "Snapchat", "Twitter", "Facebook"]
    })

    assert response.status_code == 302
    return 1


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_poll_page(client):
    response = client.get("/create")
    assert response.status_code == 200


def test_create_poll_success(client):
    response = client.post("/create", data={
        "question": "Favourite programming language?",
        "options": ["Python", "Java", "C++"]
    })

    assert response.status_code == 302

    response = client.get("/")
    assert b"Favourite programming language?" in response.data


def test_empty_question(client):
    response = client.post("/create", data={
        "question": "",
        "options": ["Python", "Java"]
    })

    assert response.status_code == 200
    assert b"Please enter a poll question." in response.data


def test_less_than_two_options(client):
    response = client.post("/create", data={
        "question": "Favourite language?",
        "options": ["Python"]
    })

    assert response.status_code == 200
    assert b"at least two options" in response.data


def test_duplicate_options(client):
    response = client.post("/create", data={
        "question": "Favourite language?",
        "options": ["Python", "python"]
    })

    assert response.status_code == 200
    assert b"Duplicate options are not allowed." in response.data


def test_empty_options_are_ignored(client):
    response = client.post("/create", data={
        "question": "Favourite language?",
        "options": ["Python", "", "Java"]
    })

    assert response.status_code == 302


def test_poll_not_found(client):
    response = client.get("/poll/999")
    assert response.status_code == 404


def test_successful_vote(client, app):
    create_test_poll(client)

    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        option_id = db.execute(
            "SELECT id FROM options WHERE poll_id = 1 LIMIT 1"
        ).fetchone()[0]
        db.close()

    response = client.post("/poll/1/vote", data={
        "voter_id": "student01",
        "option_id": str(option_id)
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Your vote was submitted successfully!" in response.data

    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        count = db.execute(
            "SELECT COUNT(*) FROM votes WHERE poll_id = 1"
        ).fetchone()[0]
        db.close()

    assert count == 1


def test_missing_voter_id(client):
    create_test_poll(client)

    response = client.post("/poll/1/vote", data={
        "option_id": "1"
    }, follow_redirects=True)

    assert b"Please enter your voter ID." in response.data


def test_missing_option(client):
    create_test_poll(client)

    response = client.post("/poll/1/vote", data={
        "voter_id": "student01"
    }, follow_redirects=True)

    assert b"Please select a valid option." in response.data


def test_invalid_option(client):
    create_test_poll(client)

    response = client.post("/poll/1/vote", data={
        "voter_id": "student01",
        "option_id": "abc"
    }, follow_redirects=True)

    assert b"Please select a valid option." in response.data


def test_option_from_another_poll(client):
    create_test_poll(client)

    client.post("/create", data={
        "question": "Favourite food?",
        "options": ["Pizza", "Burger"]
    })

    with client.application.app_context():
        db = sqlite3.connect(
            client.application.config["DATABASE"]
        )
        option_id = db.execute(
            "SELECT id FROM options WHERE poll_id = 2 LIMIT 1"
        ).fetchone()[0]
        db.close()

    response = client.post("/poll/1/vote", data={
        "voter_id": "student01",
        "option_id": str(option_id)
    }, follow_redirects=True)

    assert b"Invalid voting option." in response.data


def test_duplicate_vote(client):
    create_test_poll(client)

    client.post("/poll/1/vote", data={
        "voter_id": "student01",
        "option_id": "1"
    })

    response = client.post("/poll/1/vote", data={
        "voter_id": "student01",
        "option_id": "2"
    }, follow_redirects=True)

    assert b"You have already voted in this poll." in response.data


def test_different_voters_can_vote(client, app):
    create_test_poll(client)

    client.post("/poll/1/vote", data={
        "voter_id": "student01",
        "option_id": "1"
    })

    response = client.post("/poll/1/vote", data={
        "voter_id": "student02",
        "option_id": "2"
    }, follow_redirects=True)

    assert b"Your vote was submitted successfully!" in response.data

    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        count = db.execute(
            "SELECT COUNT(*) FROM votes WHERE poll_id = 1"
        ).fetchone()[0]
        db.close()

    assert count == 2