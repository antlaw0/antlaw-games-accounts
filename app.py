import os
from flask import Flask
from flask_cors import CORS
from models import db, migrate
from auth import auth_bp
from config import Config

port = int(os.environ.get('PORT', 5000))  # Render sets PORT

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)  # Enable CORS
db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)