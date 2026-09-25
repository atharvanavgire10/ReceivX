"""Flask serverless entry point for Vercel."""
import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from api.app.db import Base, engine
from api.app.routes import api
from api.app.seed import seed_database
from api.app.db import get_db

app = Flask(__name__)
CORS(app)
app.register_blueprint(api, url_prefix="/api")

# Create tables and seed on cold start
if engine:
    Base.metadata.create_all(bind=engine)
    try:
        db = next(get_db())
        seed_database(db)
        db.close()
    except Exception:
        pass
