# storage/movie_storage_sql.py
from sqlalchemy import create_engine, text

# SQLite DB file will be created inside data/ folder
DB_URL = "sqlite:///data/movies.db"

# echo=True prints all SQL — keep ON while developing, OFF later if noisy
engine = create_engine(DB_URL, echo=True)

# Create the tables once (safe to run multiple times)
with engine.connect() as connection:
    # Users table
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """))
    # Movies table with foreign key user_id
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(title, user_id) -- same movie allowed for different users
        )
    """))
    connection.commit()


# ---------- USER FUNCTIONS ----------

def get_all_users():
    """Return list of all users as dicts: [{'id': 1, 'name': 'John'}, ...]."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, name FROM users ORDER BY name"))
        return [{"id": row[0], "name": row[1]} for row in result.fetchall()]


def add_user(name):
    """Insert a new user. Returns the new user dict, or None if exists."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("INSERT INTO users (name) VALUES (:name)"),
                {"name": name},
            )
            connection.commit()
        except Exception as e:
            print(f"Error adding user: {e}")
            return None

        result = connection.execute(
            text("SELECT id, name FROM users WHERE name = :name"),
            {"name": name},
        ).fetchone()
        return {"id": result[0], "name": result[1]} if result else None


# ---------- MOVIE FUNCTIONS ----------

def list_movies(user_id):
    """Return movies for a specific user_id as {title: {...}}."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT title, year, rating, poster_url
            FROM movies
            WHERE user_id = :user_id
            ORDER BY title COLLATE NOCASE
        """), {"user_id": user_id})
        rows = result.fetchall()
    return {
        row[0]: {"year": row[1], "rating": row[2], "poster_url": row[3]}
        for row in rows
    }


def add_movie(user_id, title, year, rating, poster_url=None):
    """Insert a new movie for a user. Returns True on success, False on error."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                    INSERT INTO movies (title, year, rating, poster_url, user_id)
                    VALUES (:title, :year, :rating, :poster_url, :user_id)
                """),
                {"title": title, "year": year, "rating": rating,
                 "poster_url": poster_url, "user_id": user_id},
            )
            connection.commit()
            print(f"Movie '{title}' added successfully for user {user_id}.")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


def delete_movie(user_id, title):
    """Delete by title for a specific user. Returns True if something was deleted."""
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                DELETE FROM movies
                WHERE lower(title) = lower(:title) AND user_id = :user_id
            """),
            {"title": title, "user_id": user_id},
        )
        connection.commit()

    if result.rowcount > 0:
        print(f"Movie '{title}' deleted successfully for user {user_id}.")
        return True
    else:
        print(f"Movie '{title}' not found for this user.")
        return False


def update_movie(user_id, title, rating):
    """Update rating by title for a specific user. Returns True if updated."""
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                UPDATE movies
                SET rating = :rating
                WHERE lower(title) = lower(:title) AND user_id = :user_id
            """),
            {"title": title, "rating": rating, "user_id": user_id},
        )
        connection.commit()

    if result.rowcount > 0:
        print(f"Movie '{title}' updated successfully for user {user_id}.")
        return True
    else:
        print(f"Movie '{title}' not found for this user.")
        return False
