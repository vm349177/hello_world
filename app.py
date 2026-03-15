import os
import re
import sqlite3
from contextlib import closing

from flask import Flask, flash, redirect, render_template, request, url_for


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def _get_database_path() -> str:
    default_path = os.path.join(os.path.dirname(__file__), "data", "submissions.db")
    return os.environ.get("DATABASE_PATH", default_path)


def _ensure_database(db_path: str) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def _fetch_submissions(db_path: str) -> list[dict[str, str]]:
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT username, email, created_at FROM submissions ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
        return [dict(row) for row in rows]


def _insert_submission(db_path: str, username: str, email: str) -> None:
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute(
            "INSERT INTO submissions (username, email) VALUES (?, ?)",
            (username, email),
        )
        conn.commit()


def _is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(email))


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DATABASE_PATH"] = _get_database_path()
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

    _ensure_database(app.config["DATABASE_PATH"])

    @app.get("/")
    def index():
        submissions = _fetch_submissions(app.config["DATABASE_PATH"])
        return render_template("index.html", submissions=submissions)

    @app.post("/submit")
    def submit():
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()

        if not username or not email:
            flash("Please provide both a username and an email address.")
            return redirect(url_for("index"))

        if not _is_valid_email(email):
            flash("Please provide a valid email address.")
            return redirect(url_for("index"))

        _insert_submission(app.config["DATABASE_PATH"], username, email)
        flash("Thanks! Your details have been saved.")
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
