"""
app.py

Flask backend for the FAQ chatbot.

Endpoints:
  GET  /              -> API information and available endpoints
  GET  /api/health   -> simple liveness check
  GET  /api/faqs     -> list all known FAQs (useful for an admin view)
  POST /api/chat     -> { "message": "..." } -> best-matching FAQ answer
"""

"""
app.py

Flask backend for the FAQ chatbot.

Endpoints:
  GET  /              -> Serve frontend HTML page
  GET  /api/health   -> simple liveness check
  GET  /api/faqs     -> list all known FAQs (useful for an admin view)
  POST /api/chat     -> { "message": "..." } -> best-matching FAQ answer
  GET  /api/suggestions -> Get suggested questions
"""

import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from nlp_matcher import FAQMatcher

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # allow the frontend (served from a different origin/port) to call this API

FAQS_PATH = os.path.join(os.path.dirname(__file__), "faqs.json")
matcher = FAQMatcher(FAQS_PATH)


# --- SERVE FRONTEND FILES ---
@app.route("/", methods=["GET"])
def home():
    """Serve the frontend index.html"""
    return send_from_directory('../frontend', 'index.html')

@app.route("/<path:path>")
def serve_static(path):
    """Serve all static files (CSS, JS, images)"""
    return send_from_directory('../frontend', path)


# --- API ENDPOINTS ---
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "FAQ Chatbot API is running"})


@app.route("/api/faqs", methods=["GET"])
def get_faqs():
    return jsonify({"faqs": matcher.list_faqs()})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "message field is required"}), 400

    result = matcher.find_best_match(user_message)
    return jsonify(result)


@app.route("/api/suggestions", methods=["GET"])
def get_suggestions():
    """Get suggested questions for users"""
    suggestions = [
        "How do I return an item?",
        "How long does shipping take?",
        "How do I reset my password?",
        "What payment methods do you accept?",
        "How do I track my order?",
        "Do you have warranty?",
        "What's your contact number?",
        "How do I create an account?"
    ]
    return jsonify({"suggestions": suggestions})


if __name__ == "__main__":
    app.run(debug=True, port=5000)