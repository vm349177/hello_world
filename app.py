import os
import re
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    func,
    select,
)
from sqlalchemy.engine import Engine


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
METADATA = MetaData()
SUBMISSIONS_TABLE = Table(
    "submissions",
    METADATA,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(255), nullable=False),
    Column("email", String(320), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)


def _default_sqlite_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "submissions.db"


def _build_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql+psycopg://", 1)
        if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
            return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return database_url

    db_path = Path(os.environ.get("DATABASE_PATH", str(_default_sqlite_path()))).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


def _create_engine() -> Engine:
    return create_engine(_build_database_url(), future=True, pool_pre_ping=True)


def _ensure_database(engine: Engine) -> None:
    METADATA.create_all(engine)


def _fetch_submissions(engine: Engine) -> list[dict[str, str]]:
    stmt = (
        select(
            SUBMISSIONS_TABLE.c.username,
            SUBMISSIONS_TABLE.c.email,
            SUBMISSIONS_TABLE.c.created_at,
        )
        .order_by(SUBMISSIONS_TABLE.c.created_at.desc())
        .limit(20)
    )
    with engine.connect() as conn:
        rows = conn.execute(stmt).mappings().all()
    return [dict(row) for row in rows]


def _insert_submission(engine: Engine, username: str, email: str) -> None:
    with engine.begin() as conn:
        conn.execute(SUBMISSIONS_TABLE.insert().values(username=username, email=email))


def _is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(email))


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

    engine = _create_engine()
    app.config["DB_ENGINE"] = engine

    _ensure_database(engine)

    @app.get("/")
    def index():
        submissions = _fetch_submissions(app.config["DB_ENGINE"])
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

        _insert_submission(app.config["DB_ENGINE"], username, email)
        flash("Thanks! Your details have been saved.")
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
