from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import recommend_products_collaborative, recommend_products_content_based

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "L'API fonctionne ! Utilisez /recommend/collaborative ou /recommend/content"})

@app.route('/recommend/collaborative', methods=['GET'])
def recommend_collaborative():
    user_id = request.args.get('user_id')
    print(user_id)
    return jsonify({'recommendations': recommend_products_collaborative(user_id)})

@app.route('/recommend/content', methods=['GET'])
def recommend_content():
    product_desc = request.args.get('description')
    return jsonify({'recommendations': recommend_products_content_based(product_desc)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
