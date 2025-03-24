from flask import Blueprint, request, jsonify
from .agent import call_gpt4_with_function
from .models import db, UserPreference  # Import db and UserPreference from models.py

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    print("test", data)
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

@chat_bp.route("/sequence", methods=["POST"])
def generate_sequence():
    data = request.json
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

@chat_bp.route("/update_sequence", methods=["POST"])
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