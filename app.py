import os
from flask import Flask, render_template
from flask_cors import CORS
from models import db, migrate
from auth import auth_bp
from config import Config

# Create app and load config
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Initialize DB and migrations
db.init_app(app)
migrate.init_app(app, db)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")

# Routes for HTML pages
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port)
