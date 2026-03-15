import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "submissions.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test-secret")
    with app.test_client() as client:
        yield client


def test_rejects_invalid_email(client):
    response = client.post(
        "/submit",
        data={"username": "Alex", "email": "invalid"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Please provide a valid email address." in response.data


def test_accepts_valid_email_and_lists_it(client):
    response = client.post(
        "/submit",
        data={"username": "Jamie", "email": "jamie@example.com"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Thanks! Your details have been saved." in response.data

    page = client.get("/")
    assert b"jamie@example.com" in page.data