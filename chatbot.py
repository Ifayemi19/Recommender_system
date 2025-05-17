import requests
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)

CORS(app)
# URL de l'API de recommandation
RECOMMENDATION_API_BASE = "http://127.0.0.1:5001/recommend"

@app.route("/chatbot", methods=["GET"])
def chatbot():
    user_input = request.args.get("message", "").lower()

    if "recommande-moi" in user_input:
        return jsonify({"response": "Souhaitez-vous une recommandation basée sur votre historique (tapez 'collaboratif') ou sur un produit spécifique (tapez 'contenu') ?"})

    elif "collaboratif" in user_input:
        return jsonify({"response": "Entrez votre ID utilisateur pour obtenir des recommandations basées sur votre historique d'achat."})

    elif "contenu" in user_input:
        return jsonify({"response": "Décrivez un produit pour obtenir des recommandations similaires."})

    elif user_input.isdigit():  # Si l'utilisateur entre un ID utilisateur
        response = requests.get(f"{RECOMMENDATION_API_BASE}/collaborative", params={"user_id": user_input})
        return jsonify({"response": response.json()})

    elif len(user_input) > 3:  # Si l'utilisateur décrit un produit
        response = requests.get(f"{RECOMMENDATION_API_BASE}/content", params={"description": user_input})
        return jsonify({"response": response.json()})

    else:
        return jsonify({"response": "Je ne comprends pas votre demande. Essayez de demander une recommandation."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
