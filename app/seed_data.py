import requests
import random
from app.db.session import SessionLocal
from app.model.book import Book
from app.model.tag import Tag
from app.model.user import User
from app.model.book_tag import BookTag
from app.model.user_book import UserBook
from app.repo.fyb_repo import Repository
from werkzeug.security import generate_password_hash

def fetch_books_from_google(query, max_results=20):
    params = {
        "q": f"subject:{query}",
        "maxResults": max_results,
        "langRestrict": "en"
    }
    url = "https://www.googleapis.com/books/v1/volumes"

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("items", [])
    except Exception as e:
        print(f"Error ({query}): {e}")
    return []


def seed_books():
    db = SessionLocal()
    repo = Repository(db)

    # Kategori listesi
    genres = [
        "Fantasy", "Science Fiction", "Horror", "Romance", "History",
        "Mystery", "Thriller", "Biography", "Cooking", "Art", "Comics" , "Fantasy Fiction"
    ]

    print("🌱 Your library is loading...")

    for genre in genres:
        print(f"📚 The '{genre}' genre is loading...")
        books_data = fetch_books_from_google(genre, max_results=15)

        tag = repo.get_tag_by_name(genre)
        if not tag:
            tag = repo.create_tag(genre)

        for item in books_data:
            info = item.get("volumeInfo", {})
            title = info.get("title")
            if not title: continue

            book = repo.get_or_create_book(title)

            # tag eşleşmesi
            try:
                repo.add_tag_to_book(book.id, tag.id)
            except:
                db.rollback()
                pass

    print("✅ Loading books is complete.")
    db.close()

def seed_users_and_ratings():
    db = SessionLocal()
    repo = Repository(db)

    print("👤 Users are loading...")


    tags = db.query(Tag).all()
    if not tags:
        print("⚠️ Load the books first! ")
        return

    for i in range(1, 31):
        username = f"reader_{i}"

        if repo.get_user_by_name(username):
            continue

        user = repo.create_user(
            name=username,
            password_hash=generate_password_hash("1234", method='pbkdf2:sha256'),
            email=f"{username}@example.com"
        )

        favorite_tag = random.choice(tags)

        raw_ids = repo.get_book_ids_for_tags([favorite_tag.id])
        book_ids_in_genre = [r[0] for r in raw_ids]

        if not book_ids_in_genre:
            continue

        num_ratings = random.randint(5, 10)

        k = min(len(book_ids_in_genre), num_ratings)
        books_to_rate = random.sample(book_ids_in_genre, k)

        for book_id in books_to_rate:
            rating = random.choice([4.0, 4.5, 5.0])
            repo.add_or_update_user_book(user.id, book_id, rating)

    print("✅ 30 Users and their libraries have been downloaded. ")
    db.close()


if __name__ == "__main__":
    seed_books()
    seed_users_and_ratings()