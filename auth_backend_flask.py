from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import json
import os
import uuid

app = Flask(__name__)
CORS(app)

# Fichiers locaux
USER_FILE = "users.json"
CONVERSATION_FILE = "conversations.json"

# Charger les utilisateurs existants
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# Charger les conversations existantes
if os.path.exists(CONVERSATION_FILE):
    with open(CONVERSATION_FILE, "r") as f:
        conversations = json.load(f)
else:
    conversations = {}

# Utilitaire pour hasher les mots de passe
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Champs manquants"}), 400

    if username in users:
        return jsonify({"success": False, "message": "Nom d'utilisateur déjà utilisé"}), 409

    user_id = str(uuid.uuid4())
    users[username] = {"password": hash_password(password), "user_id": user_id}

    with open(USER_FILE, "w") as f:
        json.dump(users, f)

    return jsonify({"success": True, "user_id": user_id})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Champs manquants"}), 400

    user = users.get(username)
    if not user or user["password"] != hash_password(password):
        return jsonify({"success": False, "message": "Identifiants invalides"}), 401

    return jsonify({"success": True, "user_id": user["user_id"]})

@app.route("/save_conversations", methods=["POST"])
def save_conversations():
    data = request.get_json()
    user_id = data.get("user_id")
    convs = data.get("conversations")

    if not user_id or not isinstance(convs, list):
        return jsonify({"success": False, "message": "Requête invalide"}), 400

    conversations[user_id] = convs
    with open(CONVERSATION_FILE, "w") as f:
        json.dump(conversations, f)

    return jsonify({"success": True, "message": "Conversations sauvegardées"})

@app.route("/load_conversations", methods=["GET"])
def load_conversations():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "ID manquant"}), 400

    user_convs = conversations.get(user_id, [])
    return jsonify({"success": True, "conversations": user_convs})

if __name__ == "__main__":
    app.run(debug=True, port=5003)