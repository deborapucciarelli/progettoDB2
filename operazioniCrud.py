from pymongo import MongoClient


# Connessione a MongoDB Atlas
# Connessione a MongoDB (modifica la stringa con la tua password!)
#mongo_uri = "mongodb+srv://deborapucciarelli:19Pd982910@cluster0.ddwxqqr.mongodb.net/dbbook?retryWrites=true&w=majority&appName=Cluster0"
mongo_uri = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
client = MongoClient(mongo_uri)
#db = client.dbbook  # nome del tuo database
db = client.bookdb
# --------------------------
# VALIDAZIONI UTILI
# --------------------------

def is_valid_isbn(isbn):
    if not isinstance(isbn, str):
        return False
    if not (10 <= len(isbn) <= 13):
        return False
    return all(c.isalnum() for c in isbn)  # alfanumerico: lettere o numeri


def is_valid_year(year):
    return isinstance(year, int) and 1400 <= year <= 2025

def is_non_empty_text(value):
    return isinstance(value, str) and value.strip() != ""

def is_valid_user_id(user_id):
    return isinstance(user_id, int)

def is_valid_age(age):
    return isinstance(age, int) and 10 <= age <= 100

def is_valid_rating(rating):
    return isinstance(rating, int) and 1 <= rating <= 10


# --------------------------
# CLASSI PER DATI + VALIDAZIONE
# --------------------------

class Book:
    required_fields = [
        "ISBN", "Book-Title", "Book-Author", "Year-Of-Publication",
        "Publisher", "Image-URL-S", "Image-URL-M", "Image-URL-L"
    ]

    @staticmethod
    def validate(data, mode="create"):
        if mode == "create":
            for field in Book.required_fields:
                if field not in data:
                    raise ValueError(f"Campo mancante: {field}")

        isbn = str(data.get("ISBN", "")).strip()
        if not is_valid_isbn(isbn):
            raise ValueError("ISBN non valido: deve contenere solo numeri e avere lunghezza tra 10 e 13.")

        if not is_non_empty_text(data.get("Book-Title", "")):
            raise ValueError("Titolo del libro non valido.")

        if not is_non_empty_text(data.get("Book-Author", "")):
            raise ValueError("Autore del libro non valido.")

        if not is_valid_year(data.get("Year-Of-Publication", 0)):
            raise ValueError("Anno di pubblicazione non valido (deve essere tra 1400 e 2025).")

        if not is_non_empty_text(data.get("Publisher", "")):
            raise ValueError("Editore non valido.")

        for img_field in ["Image-URL-S", "Image-URL-M", "Image-URL-L"]:
            if not is_non_empty_text(data.get(img_field, "")):
                raise ValueError(f"{img_field} non valido.")


class User:
    required_fields = ["User-ID", "Location", "Age"]

    @staticmethod
    def validate(data, mode="create"):
        if mode == "create":
            for field in User.required_fields:
                if field not in data:
                    raise ValueError(f"Campo mancante: {field}")

        if not is_valid_user_id(data.get("User-ID")):
            raise ValueError("User-ID deve essere un numero intero.")

        if "Age" in data and not is_valid_age(data["Age"]):
            raise ValueError("Età non valida. Deve essere un numero tra 10 e 100.")


class Rating:
    required_fields = ["User-ID", "ISBN", "Book-Rating"]

    @staticmethod
    def validate(data, mode="create"):
        if mode == "create":
            for field in Rating.required_fields:
                if field not in data:
                    raise ValueError(f"Campo mancante: {field}")

        if not is_valid_user_id(data.get("User-ID")):
            raise ValueError("User-ID non valido. Deve essere un numero.")

        isbn = str(data.get("ISBN", "")).strip()
        if not is_valid_isbn(isbn):
            raise ValueError("ISBN non valido per rating (solo numeri, 10-13 cifre).")

        if "Book-Rating" in data and not is_valid_rating(data["Book-Rating"]):
            raise ValueError("Book-Rating deve essere un numero tra 1 e 10.")


# --------------------------
# CRUD BOOKS
# --------------------------

def create_book(book_data):
    Book.validate(book_data, mode="create")
    if db.books.find_one({"ISBN": book_data["ISBN"]}):
        raise ValueError(f"ISBN '{book_data['ISBN']}' già presente nel database. Inserire un ISBN diverso.")
    return db.books.insert_one(book_data).inserted_id

def get_book(isbn):
    isbn = isbn.strip()
    if not is_valid_isbn(isbn):
        raise ValueError("ISBN non valido per ricerca.")
    return db.books.find_one({"ISBN": isbn})

def update_book(isbn, update_data):
    isbn = isbn.strip()
    if not is_valid_isbn(isbn):
        raise ValueError("ISBN non valido per aggiornamento.")
    # Validazione campi aggiornabili
    allowed_fields = Book.required_fields.copy()
    allowed_fields.remove("ISBN")
    for key in update_data:
        if key not in allowed_fields:
            raise ValueError(f"Campo non aggiornabile: {key}")

    # Validazioni specifiche
    if "Year-Of-Publication" in update_data and not is_valid_year(update_data["Year-Of-Publication"]):
        raise ValueError("Anno di pubblicazione non valido.")
    if "Book-Title" in update_data and not is_non_empty_text(update_data["Book-Title"]):
        raise ValueError("Titolo del libro non valido.")
    if "Book-Author" in update_data and not is_non_empty_text(update_data["Book-Author"]):
        raise ValueError("Autore del libro non valido.")
    if "Publisher" in update_data and not is_non_empty_text(update_data["Publisher"]):
        raise ValueError("Editore non valido.")
    for img_field in ["Image-URL-S", "Image-URL-M", "Image-URL-L"]:
        if img_field in update_data and not is_non_empty_text(update_data[img_field]):
            raise ValueError(f"{img_field} non valido.")

    return db.books.update_one({"ISBN": isbn}, {"$set": update_data}).modified_count


def delete_book(isbn):
    result = db.books.delete_one({"ISBN": isbn})
    if result.deleted_count > 0:
        # Cancella tutte le recensioni per quel libro
        db.ratings.delete_many({"ISBN": isbn})
    return result



# --------------------------
# CRUD USERS
# --------------------------

def create_user(user_data):
    User.validate(user_data, mode="create")
    if db.users.find_one({"User-ID": user_data["User-ID"]}):
        raise ValueError(f"User-ID '{user_data['User-ID']}' già presente. Inserire un User-ID diverso.")
    return db.users.insert_one(user_data).inserted_id

def get_user(user_id):
    if not is_valid_user_id(user_id):
        raise ValueError("User-ID non valido per ricerca.")
    return db.users.find_one({"User-ID": user_id})

def update_user(user_id, update_data):
    if not is_valid_user_id(user_id):
        raise ValueError("User-ID non valido per aggiornamento.")
    # Validazioni campi aggiornabili (Location e Age)
    allowed_fields = ["Location", "Age"]
    for key in update_data:
        if key not in allowed_fields:
            raise ValueError(f"Campo non aggiornabile: {key}")
    if "Age" in update_data and not is_valid_age(update_data["Age"]):
        raise ValueError("Età non valida.")
    if "Location" in update_data and not is_non_empty_text(update_data["Location"]):
        raise ValueError("Location non valida.")
    return db.users.update_one({"User-ID": user_id}, {"$set": update_data}).modified_count

def delete_user(user_id):
    if not is_valid_user_id(user_id):
        raise ValueError("User-ID non valido per cancellazione.")
    # elimina tutte le recensioni di quell'utente
    db.ratings.delete_many({"User-ID": user_id})
    # elimina l'utente
    return db.users.delete_one({"User-ID": user_id}).deleted_count



# --------------------------
# CRUD RATINGS
# --------------------------

def create_rating(rating_data):
    Rating.validate(rating_data, mode="create")
    user_id = rating_data["User-ID"]
    isbn = rating_data["ISBN"]
    # Controlla se utente e libro esistono
    if not db.users.find_one({"User-ID": user_id}):
        raise ValueError(f"Utente {user_id} non trovato.")
    if not db.books.find_one({"ISBN": isbn}):
        raise ValueError(f"Libro con ISBN {isbn} non trovato.")
    # Controlla che la valutazione non esista già
    if db.ratings.find_one({"User-ID": user_id, "ISBN": isbn}):
        raise ValueError(f"Valutazione già esistente per utente {user_id} e libro {isbn}.")
    return db.ratings.insert_one(rating_data).inserted_id

def get_rating(user_id, isbn):
    if not is_valid_user_id(user_id) or not is_valid_isbn(isbn):
        raise ValueError("User-ID o ISBN non validi per ricerca.")
    return db.ratings.find_one({"User-ID": user_id, "ISBN": isbn})

def update_rating(user_id, isbn, new_rating):
    if not is_valid_user_id(user_id) or not is_valid_isbn(isbn) or not is_valid_rating(new_rating):
        raise ValueError("Dati non validi per aggiornamento rating.")
    return db.ratings.update_one(
        {"User-ID": user_id, "ISBN": isbn},
        {"$set": {"Book-Rating": new_rating}}
    ).modified_count

def delete_rating(user_id, isbn):
    if not is_valid_user_id(user_id) or not is_valid_isbn(isbn):
        raise ValueError("User-ID o ISBN non validi per cancellazione.")
    return db.ratings.delete_one({"User-ID": user_id, "ISBN": isbn}).deleted_count




