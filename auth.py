from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import db, User
from utils import generate_token, verify_token
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from flask_cors import cross_origin

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/register", methods=["POST", "OPTIONS"])
@cross_origin(origins="https://ai-game-azzk.onrender.com")  # Your frontend's origin
def api_register():
    print("✅ Hit /api/register route")

    # Handle CORS preflight
    if request.method == "OPTIONS":
        return '', 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        email = data.get("email")
        password = data.get("password")
        confirm = data.get("confirm") or data.get("confirm_password")

        if not email or not password or not confirm:
            return jsonify({"error": "Missing fields"}), 400
        if password != confirm:
            return jsonify({"error": "Passwords do not match"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print("❌ Registration Error:", str(e))
        return jsonify({"error": "Server error"}), 500


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
    return jsonify({
        "access_token": access_token,
        "user_id": user.id
    }), 200

@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# ✅ FIXED: Add CORS support and handle OPTIONS request
@auth_bp.route("/api/register", methods=["POST", "OPTIONS"])
@cross_origin(origins="https://ai-game-azzk.onrender.com")
def api_register():
    print("✅ Hit /api/register route")
    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    confirm = data.get("confirm") or data.get("confirm_password")

    if not email or not password or not confirm:
        return jsonify({"error": "Missing fields"}), 400
    if password != confirm:
        return jsonify({"error": "Passwords do not match"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/api/login_token", methods=["POST"])
def api_login_token():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
    return jsonify({
        "access_token": access_token,
        "user_id": user.id
    }), 200

@auth_bp.route("/api/userinfo", methods=["GET"])
@jwt_required()
def api_userinfo():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None
    })

@auth_bp.route("/api/logout", methods=["POST"])
@jwt_required()
def api_logout():
    return jsonify({"message": "Logout successful (client should delete token)"}), 200

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

@auth_bp.route("/api/reset_password", methods=["POST"])
def api_reset_password():
    data = request.get_json()
    token = data.get("token")
    password = data.get("password")
    confirm = data.get("confirm") or data.get("confirm_password")

    if not token or not password or not confirm:
        return jsonify({"error": "All fields are required"}), 400
    if password != confirm:
        return jsonify({"error": "Passwords do not match"}), 400

    user_id = verify_token(token).get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Invalid token"}), 400

    user.set_password(password)
    db.session.commit()
    return jsonify({"message": "Password reset successfully"}), 200
