from flask import Blueprint, render_template, redirect, session, url_for, request
from app.db.session import SessionLocal
from app.repo.fyb_repo import Repository
from app.service.matching_service import MatchingService

main_bp = Blueprint("main", __name__)


def require_login():
    print("AAAAAAAAAAA", "user_id" in session)
    return "user_id" in session


@main_bp.route("/")
def index():
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    service = MatchingService()

    users_books_and_ratings = service.get_users_books(user_id)

    service.db.close()

    return render_template(
        "dashboard.html",
        books_ratings=users_books_and_ratings
    )


@main_bp.route('/results', methods=['POST'])
def results():

        service = MatchingService()
        entered_books = []
        for i in range(1, 6):
            title = request.form.get(f"book{i}", "").strip()
            if not title:
                continue

            if books := service.get_possible_books(title):
                entered_books.append(books[0])

        similar_by_tags = service.recommend_by_tags(entered_books)

        similar_by_users = service.recommend_by_collaboration(entered_books)

        return render_template(
            'results.html',
            similar_by_tags=similar_by_tags,
            similar_by_users=similar_by_users
        )