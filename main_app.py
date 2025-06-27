from flask import Flask, request, jsonify
from flask import render_template
from flask_cors import CORS
import hashlib
import json
import os
import uuid
import requests


app = Flask(__name__)
CORS(app)


USER_FILE = "users.json"
CONVERSATION_FILE = "conversations.json"

from recommender import recommend_products_collaborative, recommend_products_content_based

if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}


if os.path.exists(CONVERSATION_FILE):
    with open(CONVERSATION_FILE, "r") as f:
        conversations = json.load(f)
else:
    conversations = {}


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# @app.route("/")
# def home_page():
#     return render_template("chatbot.html")

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


# @app.route('/')
# def home():
#     return jsonify({"message": "API centrale unifiée prête à fonctionner ✅"})

@app.route('/')
def home():
    return render_template("chatbot.html")


@app.route('/recommend/collaborative', methods=['GET'])
def recommend_collaborative():
    user_id = request.args.get('user_id')
    return jsonify({'recommendations': recommend_products_collaborative(user_id)})


@app.route('/recommend/content', methods=['GET'])
def recommend_content():
    product_desc = request.args.get('description')
    return jsonify({'recommendations': recommend_products_content_based(product_desc)})


@app.route("/chatbot", methods=["GET"])
def chatbot():
    user_input = request.args.get("message", "").lower()

    if "recommande-moi" in user_input:
        return jsonify({"response": "Souhaitez-vous une recommandation basée sur votre historique (tapez 'collaboratif') ou sur un produit spécifique (tapez 'contenu') ?"})

    elif "collaboratif" in user_input:
        return jsonify({"response": "Entrez votre ID utilisateur pour obtenir des recommandations basées sur votre historique d'achat."})

    elif "contenu" in user_input:
        return jsonify({"response": "Décrivez un produit pour obtenir des recommandations similaires."})

    elif user_input.isdigit():
        return jsonify({"response": recommend_products_collaborative(user_input)})

    elif len(user_input) > 3:
        return jsonify({"response": recommend_products_content_based(user_input)})

    else:
        return jsonify({"response": "Je ne comprends pas votre demande. Essayez de demander une recommandation."})


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
