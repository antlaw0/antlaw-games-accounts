import traceback
import bcrypt
from flask import request, jsonify, render_template
from itsdangerous import URLSafeTimedSerializer
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

import os
from flask import Flask, render_template
from flask_cors import CORS
from models import db, migrate
from auth import auth_bp
from config import Config

# Create app and load config
app = Flask(__name__)
app.config.from_object(Config)

serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])


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

@app.route("/send-reset-link", methods=["POST"])
def send_reset_link():
    try:
        email = request.json.get("email")
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar()

        if not user:
            return jsonify({"error": "No account found with that email"}), 404

        token = serializer.dumps(email, salt="password-reset")

        reset_link = f"{request.host_url}reset-password/{token}"

        # Send email with Brevo
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = app.config["BREVO_API_KEY"]
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

        email_content = {
            "sender": {"name": "Antlaw Games", "email": "your@email.com"},
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

        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        user.password_hash = hashed
        db.session.commit()
        return jsonify({"message": "Password has been reset."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Reset failed."}), 500


# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port)
