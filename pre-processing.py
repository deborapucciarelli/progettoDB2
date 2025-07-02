import pandas as pd
import os

# --- Caricamento ---
books = pd.read_csv("database/Books.csv", encoding='latin-1', low_memory=False)
ratings = pd.read_csv("database/Ratings.csv", encoding='latin-1')
users = pd.read_csv("database/Users.csv", encoding='latin-1')

print("Forme originali:")
print(f"📘 Books: {books.shape}")
print(f"⭐ Ratings: {ratings.shape}")
print(f"👤 Users: {users.shape}")

# --- Pulizia Books ---
books = books.dropna(subset=["ISBN", "Book-Title", "Book-Author"])  # solo i campi fondamentali
books["Year-Of-Publication"] = pd.to_numeric(books["Year-Of-Publication"], errors='coerce')
books = books[(books["Year-Of-Publication"] >= 1400) & (books["Year-Of-Publication"] <= 2025)]

# Sostituisci i campi opzionali con valori fittizi se nulli
books["Publisher"] = books["Publisher"].fillna("Unknown Publisher")
books["Image-URL-S"] = books["Image-URL-S"].fillna("N/A")
books["Image-URL-M"] = books["Image-URL-M"].fillna("N/A")
books["Image-URL-L"] = books["Image-URL-L"].fillna("N/A")

# Rimuovi duplicati ISBN
books = books.drop_duplicates(subset=["ISBN"])

# --- Pulizia Users ---
users = users.dropna(subset=["User-ID", "Location"])
users["Age"] = pd.to_numeric(users["Age"], errors='coerce')
users = users[(users["Age"] >= 10) & (users["Age"] <= 100)]
users = users.drop_duplicates(subset=["User-ID"])

# --- Filtra Ratings: ISBN validi ---
valid_isbns = set(books["ISBN"])
ratings = ratings[ratings["ISBN"].isin(valid_isbns)]

# --- Filtra Ratings: User-ID validi ---
valid_user_ids = set(users["User-ID"])
ratings = ratings[ratings["User-ID"].isin(valid_user_ids)]

# --- Rimuovi rating con valore 0 ---
ratings = ratings[ratings["Book-Rating"] > 0]

# --- Rimuovi utenti senza almeno 3 rating ---
user_rating_counts = ratings["User-ID"].value_counts()
active_users = set(user_rating_counts[user_rating_counts >= 3].index)
ratings = ratings[ratings["User-ID"].isin(active_users)]
users = users[users["User-ID"].isin(active_users)]


# --- Output finale ---
print("\n📊 Dopo la pulizia:")
print(f"Books: {books.shape}")
print(f"Ratings: {ratings.shape}")
print(f"Users: {users.shape}")

# --- Salva i file puliti ---
os.makedirs("database_clear", exist_ok=True)
books.to_csv("database_clear/Books_clean.csv", index=False)
ratings.to_csv("database_clear/Ratings_clean.csv", index=False)
users.to_csv("database_clear/Users_clean.csv", index=False)

print("\n✅ Pulizia completata. File salvati in 'database_clear'.")
