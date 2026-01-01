from flask import Blueprint, render_template, redirect, session, url_for
from app.db.session import SessionLocal
from app.repo.fyb_repo import Repository

main_bp = Blueprint("main", __name__)


def require_login():
    return "user_id" in session


@main_bp.route("/")
def index():
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    db = SessionLocal()
    repo = Repository(db)

    user_books = repo.get_books_for_user(user_id)

    db.close()

    return render_template(
        "dashboard.html",
        user_books=user_books
    )
