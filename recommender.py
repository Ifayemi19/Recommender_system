import joblib
import numpy as np
from scipy.sparse import csr_matrix
from data_processing import load_and_process_data

# 📥 Chargement des modèles et des données
print("📥 Chargement des modèles et des données...")
data, description_map, vectorizer, scaler, description_matrix = load_and_process_data()

# Chargement des modèles
model_als = joblib.load('models/model_als.pkl')
knn_model = joblib.load('models/model_knn.pkl')
stockcode_list = joblib.load('models/stockcode_list.pkl')
description_matrix = joblib.load('models/description_matrix.pkl')  # ✅ Correction

# 🔄 Reconstruction de la matrice utilisateur-produit
print("🔄 Reconstruction de la matrice utilisateur-produit...")
data = data.groupby(['customer_id', 'stockcode'], as_index=False).agg({'quantity': 'sum'})
customer_item_matrix = data.pivot(index='customer_id', columns='stockcode', values='quantity').fillna(0)

# ✅ Conversion en sparse matrix avec .tocsr()
customer_item_sparse = csr_matrix(customer_item_matrix.values).tocsr()
print(f"✅ Matrice utilisateur-produit créée avec succès ! Dimensions : {customer_item_sparse.shape}")

def recommend_products_collaborative(user_id, num_recommendations=5):
    """ Recommande des produits basés sur le filtrage collaboratif (ALS). """
    try:
        user_id = int(user_id)
        valid_user_ids = list(customer_item_matrix.index)

        if user_id not in valid_user_ids:
            return [{"error": f"Utilisateur {user_id} introuvable."}]

        # ✅ Récupérer correctement l'index utilisateur
        user_idx = valid_user_ids.index(user_id)
        print(f"📌 Index utilisateur dans la matrice ALS : {user_idx}")

        # ✅ Vérifier si ALS retourne bien des recommandations
        recommendations = model_als.recommend(user_idx, customer_item_sparse[user_idx], N=num_recommendations)

        if not recommendations:
            return [{"error": f"Aucune recommandation trouvée pour l'utilisateur {user_id}"}]

        item_indices, scores = recommendations
        recommended_items = [stockcode_list[i] for i in item_indices]

        product_descriptions = [description_map.get(item, "Description inconnue") for item in recommended_items]

        return [{"StockCode": str(item), "Description": desc} for item, desc in zip(recommended_items, product_descriptions)]
    
    except Exception as e:
        return [{"error": f"Erreur dans la recommandation collaborative : {str(e)}"}]
    
def recommend_products_content_based(product_desc, num_recommendations=5):
    """ Recommande des produits similaires basés sur leur description (KNN). """
    try:
        if not product_desc or len(product_desc.strip()) == 0:
            return [{"error": "La description du produit ne peut pas être vide"}]

        # 🔍 Transformation de la description utilisateur en vecteur TF-IDF
        transformed_desc = vectorizer.transform([product_desc])
        
        # ✅ Vérification du format des données envoyées à KNN
        print(f"📏 Dimensions du vecteur transformé : {transformed_desc.shape}")
        print(f"📏 Dimensions attendues par KNN : {knn_model._fit_X.shape}")

        # ⚠️ Vérification pour éviter les erreurs d'incompatibilité de dimensions
        if transformed_desc.shape[1] != knn_model._fit_X.shape[1]:
            return [{"error": "Le modèle KNN a été entraîné avec un nombre de caractéristiques différent"}]

        # 🔄 Trouver les voisins les plus proches
        distances, indices = knn_model.kneighbors(transformed_desc, n_neighbors=min(num_recommendations, len(stockcode_list)))

        # ✅ Vérification et correction des indices retournés
        print(f"🔍 Indices trouvés (avant correction) : {indices}")

        # Vérifier la taille réelle de stockcode_list
        print(f"📏 Taille de stockcode_list : {len(stockcode_list)}")

        # 🛠️ Filtrer les indices pour éviter les erreurs d’indexation
        valid_indices = [i for i in indices[0] if 0 <= i < len(stockcode_list)]
        print(f"🔍 Indices valides après correction : {valid_indices}")

        recommended_items = [stockcode_list[i] for i in valid_indices]
        product_descriptions = [description_map.get(item, "Description inconnue") for item in recommended_items]

        # 🚀 Retourner les recommandations sous forme JSON
        if len(recommended_items) == 0:
            return [{"error": "Aucune recommandation valide trouvée. Vérifiez l'entraînement du modèle KNN."}]
        
        return [{"StockCode": str(item), "Description": desc} for item, desc in zip(recommended_items, product_descriptions)]
    
    except Exception as e:
        return [{"error": f"Erreur dans la recommandation basée sur le contenu : {str(e)}"}]

if __name__ == "__main__":
    # 🔥 Test rapide avec un ID utilisateur existant
    print("🔍 Test des recommandations collaboratives...")
    print(recommend_products_collaborative(13085))

    print("🔍 Test des recommandations basées sur le contenu...")
    print(recommend_products_content_based("HEART FLOWER T-LIGHT HOLDER", 5))

