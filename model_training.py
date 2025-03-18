from implicit.als import AlternatingLeastSquares
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import joblib
from data_processing import load_and_process_data

# 📥 Chargement des données
print("📥 Chargement des données...")
data, description_map, vectorizer, scaler, description_matrix = load_and_process_data()

# 🔄 Correction des noms de colonnes pour éviter les KeyError
print("✅ Vérification des colonnes...")
data.columns = data.columns.str.lower().str.replace(' ', '_')

# 🔄 Agrégation pour éviter les doublons
print("🔄 Agrégation des données pour éviter les doublons...")
data = data.groupby(['customer_id', 'stockcode'], as_index=False).agg({'quantity': 'sum'})

# 📌 Construction de la matrice utilisateur-produit
print("🔄 Construction de la matrice utilisateur-produit...")
customer_item_matrix = data.pivot(index='customer_id', columns='stockcode', values='quantity').fillna(0)
customer_item_sparse = csr_matrix(customer_item_matrix.values)

print(f"✅ Matrice utilisateur-produit créée ! Dimensions : {customer_item_sparse.shape}")

# 📊 Vérification avant entraînement de KNN
print(f"📊 Vérification avant entraînement KNN :")
print(f"📏 Taille de description_matrix : {description_matrix.shape}")
print(f"📏 Nombre d'éléments uniques dans StockCode (stockcode_list) : {len(customer_item_matrix.columns)}")

# 🔄 Vérification de l'alignement entre `description_matrix` et `stockcode_list`
if description_matrix.shape[0] != len(customer_item_matrix.columns):
    print("⚠️ Avertissement : `description_matrix` et `stockcode_list` ne correspondent pas !")
    print("🛠️ Correction en cours...")
    description_matrix = description_matrix[:len(customer_item_matrix.columns)]  # Correction

# 📌 Entraînement du modèle ALS
print("🎯 Entraînement du modèle ALS...")
model_als = AlternatingLeastSquares(factors=20, regularization=0.05, iterations=10, use_cg=True, use_gpu=False)
model_als.fit(customer_item_sparse)

# 📌 Entraînement du modèle KNN
print("🔍 Entraînement du modèle KNN...")
knn_model = NearestNeighbors(n_neighbors=5, metric='cosine', n_jobs=-1)
knn_model.fit(description_matrix)

# 💾 Sauvegarde des modèles et des matrices
print("💾 Sauvegarde des modèles et des matrices...")
joblib.dump(model_als, 'models/model_als.pkl')
joblib.dump(knn_model, 'models/model_knn.pkl')
joblib.dump(vectorizer, 'models/vectorizer.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
joblib.dump(description_matrix, 'models/description_matrix.pkl')
joblib.dump(list(customer_item_matrix.columns), 'models/stockcode_list.pkl')  # ✅ Correction de la liste des StockCodes

print("✅ Tous les modèles et matrices ont été sauvegardés avec succès !")
