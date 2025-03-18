import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer

def load_and_process_data():
    print("📥 Chargement des fichiers CSV...")
    cols_to_use = ['Customer ID', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'Price']

    df1 = pd.read_csv("data/Year 2009-2010.csv", usecols=cols_to_use, encoding='latin1', sep=';', quotechar='"', on_bad_lines='skip')
    df2 = pd.read_csv("data/Year 2010-2011.csv", usecols=cols_to_use, encoding='latin1', sep=';', quotechar='"', on_bad_lines='skip')
    data = pd.concat([df1, df2], ignore_index=True)

    # Normaliser les noms de colonnes
    data.columns = data.columns.str.lower().str.replace(" ", "_")

    # Nettoyage des données
    data.dropna(subset=['customer_id', 'stockcode', 'description'], inplace=True)
    data['customer_id'] = data['customer_id'].astype(int)
    data['stockcode'] = data['stockcode'].astype(str)
    data['invoicedate'] = pd.to_datetime(data['invoicedate'])
    data = data[data['quantity'] > 0]
    data = data[data['price'] > 0]

    # Filtrage des utilisateurs et produits les plus actifs
    user_counts = data['customer_id'].value_counts()
    data = data[data['customer_id'].isin(user_counts[user_counts > 10].index)]
    product_counts = data['stockcode'].value_counts()
    data = data[data['stockcode'].isin(product_counts[product_counts > 20].index)]

    # Transformation des descriptions en vecteurs TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    description_map = data.groupby('stockcode')['description'].first().to_dict()
    description_matrix = vectorizer.fit_transform([description_map.get(sc, '') for sc in data['stockcode']])

    scaler = MinMaxScaler()
    data[['quantity']] = scaler.fit_transform(data[['quantity']])

    return data, description_map, vectorizer, scaler, description_matrix
