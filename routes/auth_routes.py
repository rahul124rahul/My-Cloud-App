from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

from aws.dynamodb_service import create_user, get_user_by_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        existing_user = get_user_by_email(email)

        if existing_user:
            return "User already exists"

        password_hash = generate_password_hash(password)

        create_user(email, password_hash)

        return redirect("/login")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = get_user_by_email(email)

        if user and check_password_hash(user["password_hash"], password):

            session["user_id"] = user["user_id"]
            session["email"] = user["email"]

            return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/login")