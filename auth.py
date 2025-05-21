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

@auth_bp.route("/register", methods=["POST"])
def register():
    data = get_form_data()

    if not data:
        return jsonify({"error": "Invalid request data"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    # For HTML form, redirect. Otherwise, return JSON.
    if request.headers.get("Accept") == "application/json":
        return jsonify({"message": "Registered successfully"})
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
