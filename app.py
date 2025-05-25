from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")  # Replace with a secure key
CORS(app, origins=['https://ai-game-azzk.onrender.com'])  # Replace with your actual AI game URL

# In-memory user storage for demonstration purposes
users = {}

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not email or not password or not confirm_password:
        return jsonify({'error': 'Missing fields'}), 400
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400
    if email in users:
        return jsonify({'error': 'Email already registered'}), 400

    hashed_password = generate_password_hash(password)
    users[email] = {'password': hashed_password}
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users.get(email)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt.encode({
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token}), 200

@app.route('/api/user', methods=['GET'])
def get_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Authorization header missing'}), 401

    token = auth_header.split(" ")[1]
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        email = data['email']
        if email not in users:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'email': email}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
