from implicit.als import AlternatingLeastSquares
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import joblib
from data_processing import load_and_process_data

print("📥 Chargement des données...")
data, description_map, vectorizer, scaler, description_matrix = load_and_process_data()

# Agrégation pour éviter les doublons
print("🔄 Agrégation des données pour éviter les doublons...")
data = data.groupby(['customer_id', 'stockcode'], as_index=False).agg({'quantity': 'sum'})

# Construction de la matrice utilisateur-produit
print("🔄 Construction de la matrice utilisateur-produit...")
customer_item_matrix = data.pivot(index='customer_id', columns='stockcode', values='quantity').fillna(0)
customer_item_sparse = csr_matrix(customer_item_matrix.values)

print(f"✅ Matrice utilisateur-produit créée ! Dimensions : {customer_item_sparse.shape}")

# Entraînement du modèle ALS
print("🎯 Entraînement du modèle ALS...")
model_als = AlternatingLeastSquares(factors=20, regularization=0.05, iterations=10, use_cg=True, use_gpu=False)
model_als.fit(customer_item_sparse)

# Entraînement du modèle KNN
print("🔍 Entraînement du modèle KNN...")
knn_model = NearestNeighbors(n_neighbors=5, metric='cosine', n_jobs=-1)
knn_model.fit(description_matrix)

# 📂 Sauvegarde du modèle KNN et des autres données nécessaires
print("💾 Sauvegarde des modèles et des matrices...")
joblib.dump(model_als, 'models/model_als.pkl')
joblib.dump(knn_model, 'models/model_knn.pkl')
joblib.dump(vectorizer, 'models/vectorizer.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
joblib.dump(description_matrix, 'models/description_matrix.pkl')  # ✅ Sauvegarde ajoutée
joblib.dump(list(customer_item_matrix.columns), 'models/stockcode_list.pkl')  # ✅ Correction stockcodes

print("✅ Tous les modèles et matrices ont été sauvegardés avec succès !")
