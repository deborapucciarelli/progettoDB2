import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0")
db = client.bookdb

books = pd.read_csv("database_clear/Books_clean.csv")
ratings = pd.read_csv("database_clear/Ratings_clean.csv")
users = pd.read_csv("database_clear/Users_clean.csv")

db.books.insert_many(books.to_dict(orient="records"))
db.ratings.insert_many(ratings.to_dict(orient="records"))
db.users.insert_many(users.to_dict(orient="records"))

print("✅ Dati puliti importati con successo.")

# --- Conteggio documenti per collezione ---
print(f"📚 Books inseriti: {db.books.count_documents({})}")
print(f"👥 Users inseriti: {db.users.count_documents({})}")
print(f"⭐ Ratings inseriti: {db.ratings.count_documents({})}")