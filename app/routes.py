from flask import Blueprint, render_template, redirect, session, url_for, request
from app.db.session import SessionLocal
from app.repo.fyb_repo import Repository
from app.service.matching_service import MatchingService

main_bp = Blueprint("main", __name__)


def require_login():
    # Kullanıcı ID'si varsa YA DA misafir modu açıksa giriş başarılıdır
    return "user_id" in session or session.get("is_guest")


@main_bp.route("/")
def index():
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("auth.login"))

    # Misafir kontrolü
    is_guest = session.get("is_guest", False)
    users_books_and_ratings = []

    # Eğer misafir DEĞİLSE, kitaplarını veritabanından çek
    if not is_guest:
        user_id = session["user_id"]
        service = MatchingService()
        users_books_and_ratings = service.get_users_books(user_id)
        service.db.close()

    return render_template(
        "dashboard.html",
        books_ratings=users_books_and_ratings,
        is_guest=is_guest  # HTML sayfasına misafir olup olmadığını söylüyoruz
    )


@main_bp.route('/results', methods=['POST'])
def results():
    if not require_login():
        return redirect(url_for("auth.login"))

    service = MatchingService()
    entered_books = []
    for i in range(1, 6):
        title = request.form.get(f"book{i}", "").strip()
        if not title:
            continue

        if books := service.get_possible_books(title):
            entered_books.append(books[0])

    # Tag bazlı öneriler herkes için çalışır
    similar_by_tags = service.recommend_by_tags(entered_books)

    # Kullanıcı bazlı öneriler sadece giriş yapmış üyeler için çalışır
    similar_by_users = []
    user_id = session.get("user_id")

    if user_id:
        similar_by_users = service.recommend_by_users(user_id, entered_books)
    else:
        similar_by_users = [ "For a personalised list please login first" ]

    return render_template(
        'results.html',
        similar_by_tags=similar_by_tags,
        similar_by_users=similar_by_users
    )


@main_bp.route("/add-book", methods=["POST"])
def add_book():
    if session.get("is_guest"):
        return redirect(url_for("auth.login"))

    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    title = request.form["title"].strip()

    # int yerine float
    rating = float(request.form["rating"])

    service = MatchingService()

    # 🔑 get or create
    book = service.repo.get_or_create_book(title)

    service.repo.add_or_update_user_book(
        user_id=user_id,
        book_id=book.id,
        rating=rating
    )

    return redirect("/dashboard")


@main_bp.route("/delete-book", methods=["POST"])
def delete_book():
    if session.get("is_guest"):
        return redirect(url_for("auth.login"))

    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    book_id = int(request.form["book_id"])

    service = MatchingService()
    service.repo.delete_user_book(user_id, book_id)

    return redirect("/dashboard")