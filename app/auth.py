from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app.db.session import SessionLocal
from app.repo.fyb_repo import Repository
from werkzeug.security import generate_password_hash, check_password_hash

from app.service.security_service import SecurityService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method != "POST":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    service = SecurityService()
    user = service.get_user_by_name(username)
    if not user or not check_password_hash(user.password_hash, password):
        flash("Invalid username or password")
        return redirect(url_for("auth.login"))

    session["user_id"] = user.id

    return redirect(url_for("main.dashboard"))



@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method != "POST":
        return render_template("signup.html")

    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]

    service = SecurityService()

    if service.get_user_by_name(username):
        flash("Username already exists")
        return redirect(url_for("auth.signup"))

    password_hash = generate_password_hash(password)
    service.create_user(username, password_hash, email)

    flash("Account created. Please log in.")
    return redirect(url_for("auth.login"))



@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
