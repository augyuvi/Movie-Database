# movie_storage_sql.py
from sqlalchemy import create_engine, text

# SQLite DB file will be created in the current working directory
DB_URL = "sqlite:///movies.db"

# echo=True prints all SQL — keep ON while developing, OFF later if noisy
engine = create_engine(DB_URL, echo=True)

# Create the table once (safe to run multiple times)
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT
        )
    """))
    connection.commit()


def list_movies():
    """Return {title: {'year': int, 'rating': float, 'poster_url': str}, ...}."""
    with engine.connect() as connection:
        result = connection.execute(text(
            "SELECT title, year, rating, poster_url FROM movies ORDER BY title COLLATE NOCASE"
        ))
        rows = result.fetchall()
    return {
        row[0]: {"year": row[1], "rating": row[2], "poster_url": row[3]}
        for row in rows
    }


def add_movie(title, year, rating, poster_url=None):
    """Insert a new movie (with poster). Returns True on success, False on error."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                    INSERT INTO movies (title, year, rating, poster_url)
                    VALUES (:title, :year, :rating, :poster_url)
                """),
                {"title": title, "year": year, "rating": rating, "poster_url": poster_url},
            )
            connection.commit()
            print(f"Movie '{title}' added successfully.")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


def delete_movie(title):
    """Delete by title (case-insensitive). Returns True if something was deleted."""
    with engine.connect() as connection:
        result = connection.execute(
            text("DELETE FROM movies WHERE lower(title) = lower(:title)"),
            {"title": title},
        )
        connection.commit()

    if result.rowcount > 0:
        print(f"Movie '{title}' deleted successfully.")
        return True
    else:
        print(f"Movie '{title}' not found.")
        return False


def update_movie(title, rating):
    """Update rating by title (case-insensitive). Returns True if updated."""
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                UPDATE movies
                SET rating = :rating
                WHERE lower(title) = lower(:title)
            """),
            {"title": title, "rating": rating},
        )
        connection.commit()

    if result.rowcount > 0:
        print(f"Movie '{title}' updated successfully.")
        return True
    else:
        print(f"Movie '{title}' not found.")
        return False
