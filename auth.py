from flask import Blueprint, request, jsonify
from models import db, User
from utils import generate_token, verify_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400
    user = User(email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registered successfully"})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if user and user.check_password(data["password"]):
        token = generate_token(user.id)
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/verify_token", methods=["POST"])
def verify():
    data = request.json
    payload = verify_token(data["token"])
    if payload:
        return jsonify({"user_id": payload["user_id"]})
    return jsonify({"error": "Invalid token"}), 401
