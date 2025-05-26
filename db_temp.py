# reset_db.py
import os
from flask import Flask
from models import db
theDB="postgresql://antlawgames-accounts_owner:npg_W8cH2SGMgDVY@ep-empty-hat-a5nohn1r-pooler.us-east-2.aws.neon.tech/antlawgames-accounts?sslmode=require"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = theDB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Neon DB reset complete.")
