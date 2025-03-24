import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Blueprint, request, jsonify
from .agent import call_gpt4_with_function
from .models import db, UserPreference  # Import db and UserPreference from models.py

# db = SQLAlchemy()
app = Flask(__name__)
#new addition
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    print("test in Helix", data)
    message = data.get("message", "")
    history = data.get("history", [])
    user_id = data.get("user_id", "default_user")  # Add user_id for compatibility

    # Save user preferences to the database
    preference = UserPreference.query.filter_by(user_id=user_id).first()
    if not preference:
        preference = UserPreference(user_id=user_id, preferences=message)
        db.session.add(preference)
    else:
        preference.preferences = message
    db.session.commit()

    result = call_gpt4_with_function(message, history)
    return jsonify(result)

# @csrf.exempt
@app.route("/api/sequence", methods=["POST"])
def generate_sequence():
    print("🔁 /api/sequence hit")
    data = request.json
    print("Received data:", data)
    user_id = data.get("user_id", "default_user")
    preferences = data.get("preferences", "")

    # Generate sequence using GPT-4
    sequence_prompt = f"Generate a 3-step email outreach sequence for recruiting candidates based on the following preferences: {preferences}. Format each step as: '1. Subject: [Subject]\n[Body]\n\n2. Follow-Up (3 days later)\nSubject: [Subject]\n[Body]\n\n3. Final Follow-Up (1 week later)\nSubject: [Subject]\n[Body]'"
    sequence = call_gpt4_with_function(sequence_prompt, [])

    # Save the sequence to the database
    preference = UserPreference.query.filter_by(user_id=user_id).first()
    if preference:
        preference.sequence = sequence["response"]
        db.session.commit()

    return jsonify({"sequence": sequence["response"]})

@app.route("/api/update_sequence", methods=["POST"])
def update_sequence():
    data = request.json
    user_id = data.get("user_id", "default_user")
    sequence = data.get("sequence", "")

    # Update the sequence in the database
    preference = UserPreference.query.filter_by(user_id=user_id).first()
    if preference:
        preference.sequence = sequence
        db.session.commit()

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)