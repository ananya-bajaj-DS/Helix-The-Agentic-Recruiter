from flask_sqlalchemy import SQLAlchemy

# Initialize db (it will be configured in run.py)
db = SQLAlchemy()

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    preferences = db.Column(db.Text, nullable=False)
    sequence = db.Column(db.Text, nullable=True)