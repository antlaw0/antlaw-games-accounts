import os
import traceback
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_login import LoginManager, current_user

from itsdangerous import URLSafeTimedSerializer
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv
from models import db, migrate, User
from auth import auth_bp
from config import Config
from werkzeug.security import generate_password_hash

load_dotenv()

# Create app and load config
app = Flask(__name__)
app.config.from_object(Config)
app.config["BREVO_API_KEY"] = os.getenv("BREVO_API_KEY")

# Enable CORS
CORS(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Register user_loader for flask-login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Initialize DB and migrations
db.init_app(app)
migrate.init_app(app, db)

# Serializer for secure tokens
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# Register authentication blueprint
app.register_blueprint(auth_bp, url_prefix="/auth")

# Routes for HTML pages
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/send-reset-link", methods=["POST"])
def send_reset_link():
    try:
        email = request.json.get("email")
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar()

        if not user:
            return jsonify({"error": "No account found with that email"}), 404

        token = serializer.dumps(email, salt="password-reset")
        reset_link = f"{request.host_url}reset-password/{token}"

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = app.config["BREVO_API_KEY"]
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

        email_content = {
            "sender": {"name": "Antlaw Games", "email": "antlawgames@gmail.com"},
            "to": [{"email": email}],
            "subject": "Password Reset Request",
            "htmlContent": f"""
                <p>Click the link below to reset your password:</p>
                <a href="{reset_link}">{reset_link}</a>
                <p>This link will expire in 1 hour.</p>
            """,
        }

        api_instance.send_transac_email(email_content)
        return jsonify({"message": "Reset link sent!"})
    except ApiException as e:
        print(e)
        return jsonify({"error": "Email sending failed."}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.route("/reset-password/<token>", methods=["GET"])
def reset_password_page(token):
    try:
        email = serializer.loads(token, salt="password-reset", max_age=3600)
        return render_template("reset_password.html", token=token)
    except Exception:
        return "The reset link is invalid or has expired."

@app.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset", max_age=3600)
        new_password = request.json.get("password")

        if not new_password:
            return jsonify({"error": "Password required"}), 400

        user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.set_password(new_password)
        db.session.commit()

        return jsonify({"message": "Password has been reset."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Reset failed."}), 500

from flask_login import login_required

@app.route("/whoami")
@login_required
def whoami():
    return f"You are logged in as {current_user.email}"

print("SECRET_KEY loaded:", app.config["SECRET_KEY"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
