from pymongo import MongoClient

#mongo_uri = "mongodb+srv://deborapucciarelli:19Pd982910@cluster0.ddwxqqr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_uri = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
client = MongoClient(mongo_uri)
#db = client.dbbook
db = client.bookdb

#join books + ratings

def get_book_with_ratings(isbn):
    pipeline = [
        {"$match": {"ISBN": isbn}},
        {"$lookup": {
            "from": "ratings",
            "localField": "ISBN",
            "foreignField": "ISBN",
            "as": "ratings"
        }}
    ]
    result = list(db.books.aggregate(pipeline))
    return result[0] if result else None


#join tra utenti e ratings

def get_user_with_ratings(user_id):
    user = db.users.find_one({"User-ID": user_id})
    if not user:
        return "not_found"  # caso 1: utente non esiste

    pipeline = [
        {"$match": {"User-ID": user_id}},
        {
            "$lookup": {
                "from": "ratings",
                "localField": "User-ID",
                "foreignField": "User-ID",
                "as": "ratings"
            }
        },
        {
            "$addFields": {
                "num_ratings": {"$size": "$ratings"}
            }
        },
        {
            "$match": {
                "num_ratings": {"$gte": 3}
            }
        },
        {
            "$project": {
                "_id": 1,
                "User-ID": 1,
                "Location": 1,
                "Age": 1,
                "ratings": 1
            }
        }
    ]
    results = list(db.users.aggregate(pipeline))
    if results:
        return results[0]  # caso OK
    else:
        return "few_ratings"  # caso 2: utente ha meno di 3 recensioni







