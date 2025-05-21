from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from models import db, User
from utils import generate_token, verify_token

auth_bp = Blueprint("auth", __name__)

def get_form_data():
    """Helper to handle both JSON and form submissions."""
    return request.get_json() or request.form

@auth_bp.route("/register", methods=["POST"])
def register():
    data = get_form_data()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registered successfully"})

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = get_form_data()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        if request.headers.get("Accept") == "application/json":
            return jsonify({"error": "Email and password required"}), 400
        flash("Email and password required.")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        token = generate_token(user.id)
        session["user_id"] = user.id

        if request.headers.get("Accept") == "application/json":
            return jsonify({"token": token})

        return redirect(url_for("index"))
    else:
        if request.headers.get("Accept") == "application/json":
            return jsonify({"error": "Invalid credentials"}), 401
        flash("Invalid email or password.")
        return redirect(url_for("auth.login"))

@auth_bp.route("/verify_token", methods=["POST"])
def verify():
    data = get_form_data()
    token = data.get("token")

    if not token:
        return jsonify({"error": "Token is required"}), 400

    payload = verify_token(token)
    if payload:
        return jsonify({"user_id": payload["user_id"]}), 200

    return jsonify({"error": "Invalid token"}), 401
