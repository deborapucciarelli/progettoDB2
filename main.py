from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import operazioniCrud
import operazioniJoin

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

#mongo_uri = "mongodb+srv://deborapucciarelli:19Pd982910@cluster0.ddwxqqr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_uri = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
client = MongoClient(mongo_uri)
db = client.bookdb

app = Flask(__name__)
CORS(app)

# --- BOOKS ---
@app.route('/books/<isbn>', methods=['GET'])
def get_book(isbn):
    isbn = isbn.strip()
    book = operazioniCrud.get_book(isbn)
    if book:
        book['_id'] = str(book['_id'])
        response = jsonify(book)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    return jsonify({"error": "Libro non trovato"}), 404

@app.route("/api/books/isbns", methods=["GET"])
def get_isbns():
    isbns_cursor = db.books.find({}, {"ISBN": 1, "_id": 0})
    isbn = [book["ISBN"] for book in isbns_cursor if "ISBN" in book]
    response = jsonify(isbn)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/api/books/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    isbn = isbn.strip()
    book = operazioniCrud.get_book(isbn)
    if book:
        book['_id'] = str(book['_id'])
        response = jsonify(book)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    else:
        return jsonify({}), 404

@app.route("/api/books/isbns/search", methods=["GET"])
def search_isbns():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])
    regex = {"$regex": query, "$options": "i"}
    matched_books = db.books.find({"ISBN": regex}, {"ISBN": 1, "_id": 0}).limit(20)
    result = [book["ISBN"] for book in matched_books]
    response = jsonify(result)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/books', methods=['GET'])
def get_all_books():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit
    books_cursor = db.books.find().skip(skip).limit(limit)
    books = list(books_cursor)
    for book in books:
        book['_id'] = str(book['_id'])
    response = jsonify(books)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/books', methods=['POST'])
def create_book():
    book_data = request.json
    try:
        operazioniCrud.create_book(book_data)
        response = jsonify({"message": "Libro creato"})
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response, 201
    except DuplicateKeyError:
        response = jsonify({"error": "ISBN già presente"})
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response, 409
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response, 500

@app.route('/books/<isbn>', methods=['PUT'])
def update_book(isbn):
    update_data = request.json
    operazioniCrud.update_book(isbn, update_data)
    response = jsonify({"message": "Libro aggiornato"})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/books/<isbn>', methods=['DELETE'])
def delete_book_route(isbn):
    try:
        result = operazioniCrud.delete_book(isbn)
        if result.deleted_count == 0:
            response = jsonify({"error": "Libro non trovato"})
            response.headers["Content-Type"] = "application/json; charset=utf-8"
            return response, 404
        response = jsonify({"message": "Libro cancellato"})
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response, 200
    except Exception as e:
        response = jsonify({"error": "Errore interno"})
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response, 500

# --- USERS ---
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = operazioniCrud.get_user(user_id)
    if user:
        user['_id'] = str(user['_id'])
        response = jsonify(user)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    response = jsonify({"error": "Utente non trovato"})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response, 404

@app.route('/users', methods=['GET'])
def get_all_users():
    users = list(db.users.find())
    for user in users:
        user['_id'] = str(user['_id'])
    response = jsonify(users)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/api/users/userids', methods=['GET'])
def get_user_ids():
    user_ids = list(db.users.find({}, {"User-ID": 1, "_id": 0}))
    user_ids_list = [u["User-ID"] for u in user_ids]
    response = jsonify(user_ids_list)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json
    operazioniCrud.create_user(user_data)
    response = jsonify({"message": "Utente creato"})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response, 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    update_data = request.json
    operazioniCrud.update_user(user_id, update_data)
    response = jsonify({"message": "Utente aggiornato"})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    operazioniCrud.delete_user(user_id)
    response = jsonify({"message": "Utente cancellato"})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

# --- RATINGS ---
@app.route('/ratings/<int:user_id>/<isbn>', methods=['GET'])
def get_rating(user_id, isbn):
    rating = operazioniCrud.get_rating(user_id, isbn)
    if rating:
        rating['_id'] = str(rating['_id'])
        response = jsonify(rating)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    response = jsonify({"error": "Valutazione non trovata"})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response, 404

@app.route('/ratings', methods=['GET'])
def get_all_ratings():
    ratings = list(db.ratings.find())
    for rating in ratings:
        rating['_id'] = str(rating['_id'])
    response = jsonify(ratings)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/ratings', methods=['POST'])
def create_rating():
    rating_data = request.json
    operazioniCrud.create_rating(rating_data)
    response = jsonify({"message": "Valutazione creata"})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response, 201

@app.route('/ratings/<int:user_id>/<isbn>', methods=['PUT'])
def update_rating(user_id, isbn):
    update_data = request.json
    new_rating = update_data.get("Book-Rating")
    operazioniCrud.update_rating(user_id, isbn, new_rating)
    response = jsonify({"message": "Valutazione aggiornata"})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/ratings/<int:user_id>/<isbn>', methods=['DELETE'])
def delete_rating(user_id, isbn):
    operazioniCrud.delete_rating(user_id, isbn)
    response = jsonify({"message": "Valutazione cancellata"})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

# --- JOIN ---
@app.route('/books/<isbn>/ratings', methods=['GET'])
def get_book_ratings(isbn):
    book_with_ratings = operazioniJoin.get_book_with_ratings(isbn.strip())
    if book_with_ratings:
        book_with_ratings['_id'] = str(book_with_ratings['_id'])
        for rating in book_with_ratings.get('ratings', []):
            rating['_id'] = str(rating['_id'])
        response = jsonify(book_with_ratings)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    response = jsonify({"error": "Libro non trovato"})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response, 404


@app.route('/users/<int:user_id>/ratings', methods=['GET'])
def get_user_ratings(user_id):
    user_with_ratings = operazioniJoin.get_user_with_ratings(user_id)
    
    if user_with_ratings == "not_found":
        return jsonify({"error": "Utente non trovato"}), 404
    elif user_with_ratings == "few_ratings":
        return jsonify({"error": "L'utente ha meno di 3 recensioni"}), 400

    user_with_ratings['_id'] = str(user_with_ratings['_id'])
    for rating in user_with_ratings.get('ratings', []):
        rating['_id'] = str(rating['_id'])
    response = jsonify(user_with_ratings)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response



#Aggregazioni top50 libri 
@app.route("/books/top10", methods=["GET"])
def get_top_10_books():
    pipeline = [
        {"$group": {"_id": "$ISBN", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$lookup": {
            "from": "books",
            "localField": "_id",
            "foreignField": "ISBN",
            "as": "book_info"
        }},
        {"$unwind": "$book_info"},
        {"$group": {
            "_id": "$_id",
            "count": {"$first": "$count"},
            "title": {"$first": "$book_info.Book-Title"},
            "author": {"$first": "$book_info.Book-Author"}
        }},
        {"$sort": {"count": -1}},  # ordinamento finale decrescente
        {"$project": {
            "_id": 0,
            "ISBN": "$_id",
            "title": 1,
            "author": 1,
            "count": 1
        }}
    ]
    results = list(db.ratings.aggregate(pipeline))
    return jsonify(results)

#aggregazione recensioni
@app.route('/ratings/distribution', methods=['GET'])
def ratings_distribution():
    pipeline = [
        {
            "$group": {
                "_id": "$Book-Rating",
                "count": {"$sum": 1}
            }
        }
    ]

    result = list(db.ratings.aggregate(pipeline))

    # Creiamo un dizionario con tutte le valutazioni da 1 a 10, anche se zero
    distribution = {str(i): 0 for i in range(1, 11)}

    for doc in result:
        rating = str(doc["_id"])
        count = doc["count"]
        distribution[rating] = count

    # Ordiniamo la distribuzione da 10 a 1 (opzionale)
    distribution = dict(sorted(distribution.items(), key=lambda x: int(x[0]), reverse=True))

    return jsonify(distribution)

#prova
@app.route('/test-replica', methods=['GET'])
def test_replica():
    try:
        ismaster = client.admin.command("ismaster")
        primary = ismaster.get("primary", "unknown")
        count_books = db.books.count_documents({})
        return jsonify({
            "primary_node": primary,
            "books_count": count_books
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
