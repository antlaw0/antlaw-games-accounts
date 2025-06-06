from flask import Flask, request, jsonify
from extensions import db
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
from datetime import datetime, timedelta

import logging
logging.getLogger('flask_cors').level = logging.DEBUG

# Initialize app and configs
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5001", "https://your-production-frontend.com"]}}, supports_credentials=True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True
}

# tempoarily allowing all since in local testing
#CORS(app, origins=['https://ai-game-azzk.onrender.com'], supports_credentials=True)

db.init_app(app)

# Import model AFTER db.init_app to avoid circular import
from models import User




@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    print("Received data:", data)
    email = data.get('email')
    password = data.get('password')
    confirm = data.get('confirm')

    print("email:", email)
    print("password:", password)
    print("confirm:", confirm)

    if not email or not password or not confirm:
        return jsonify({'error': 'Missing fields'}), 400

    if password != confirm:
        return jsonify({'error': 'Passwords do not match'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    hashed_password = generate_password_hash(password)

    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Account created successfully'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing fields'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token_payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'Login successful', 'token': token}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
