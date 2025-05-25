from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db
from auth import auth_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your-jwt-secret"

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
jwt = JWTManager(app)

# ✅ CORS now allows requests from AI game site
CORS(app, resources={r"/api/*": {"origins": "https://ai-game-azzk.onrender.com"}})

app.register_blueprint(auth_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)