from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from models import db, User
from utils import generate_token, verify_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    data = request.get_json() if request.is_json else request.form
    if not data:
        return jsonify({"error": "No data received"}), 400

    email = data.get("email")
    password = data.get("password")
    confirm = data.get("confirm") or data.get("confirm_password")

    if not email or not password or not confirm:
        return jsonify({"error": "Email and password fields are required"}), 400
    if password != confirm:
        return jsonify({"error": "Passwords do not match"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    if request.headers.get("Accept") != "application/json":
        return redirect(url_for("auth.login"))
    return jsonify({"message": "Registered successfully"}), 200

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash("Login successful!")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password.")
            return redirect(url_for("auth.login"))

    if "user_id" in session:
        return redirect(url_for("index"))

    return render_template("login.html")

@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@auth_bp.route("/verify_token", methods=["POST"])
def verify():
    data = request.get_json() or request.form
    token = data.get("token")
    if not token:
        return jsonify({"error": "Token is required"}), 400

    payload = verify_token(token)
    if payload:
        return jsonify({"user_id": payload["user_id"]}), 200
    return jsonify({"error": "Invalid token"}), 401
