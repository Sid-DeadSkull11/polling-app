
import pytest
from app import create_app


@pytest.fixture
def client(tmp_path):
    database = tmp_path / "test_polls.db"

    app = create_app({
        "TESTING": True,
        "DATABASE": str(database),
        "SECRET_KEY": "test-secret"
    })

    with app.test_client() as client:
        yield client


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_poll_page(client):
    response = client.get("/create")
    assert response.status_code == 200


def test_create_poll_success(client):
    response = client.post("/create", data={
        "question": "Which language do you prefer?",
        "options": ["Python", "Java", "C++"]
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Poll created successfully" in response.data
    assert b"Python" in response.data


def test_empty_question(client):
    response = client.post("/create", data={
        "question": "",
        "options": ["Python", "Java"]
    })
    assert b"Please enter a poll question" in response.data


def test_less_than_two_options(client):
    response = client.post("/create", data={
        "question": "Choose a language",
        "options": ["Python"]
    })
    assert b"at least two options" in response.data


def test_duplicate_options(client):
    response = client.post("/create", data={
        "question": "Choose a language",
        "options": ["Python", "python"]
    })
    assert b"Duplicate options are not allowed" in response.data


def test_empty_options_are_ignored(client):
    response = client.post("/create", data={
        "question": "Choose a language",
        "options": ["Python", "", "Java"]
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Python" in response.data
    assert b"Java" in response.data


def test_poll_not_found(client):
    response = client.get("/poll/999")
    assert response.status_code == 404