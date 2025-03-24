from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    # Allow CORS for requests from http://localhost:5173, including preflight requests
    CORS(app, resources={
            r"/api/*": {
                "origins": "http://localhost:5173",
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import chat_bp
    app.register_blueprint(chat_bp, url_prefix="/api")

    return app