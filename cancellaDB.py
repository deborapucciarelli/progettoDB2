from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0")
db = client.bookdb

db.books.delete_many({})
db.ratings.delete_many({})
db.users.delete_many({})

print("📛 Tutte le collezioni svuotate.")
