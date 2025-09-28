# ---------------------------------------------------------
# movies.py
# Main entry point for the Movie Database project
# Updated for Codio BONUS part: User Profiles
# ---------------------------------------------------------

from __future__ import annotations
import random

import storage.movie_storage_sql as storage   # switched from JSON to SQL storage
import website_generator                      # for generating website


# Simple ANSI colors for nicer terminal output
RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
CYAN    = "\033[36m"
MAGENTA = "\033[35m"

# Track the currently logged-in user (set in select_user)
current_user_id: int | None = None
current_username: str | None = None


# ---------- USER HANDLING ----------

def select_user() -> None:
    """
    Handles profile selection.
    - Lists all existing users.
    - Lets the user pick or create a new profile.
    - Updates the global variables current_user_id and current_username.
    """
    global current_user_id, current_username

    users = storage.get_all_users()
    if not users:
        print(f"{YELLOW}No users yet. Please create one.{RESET}")
        name = input("Enter new user name: ").strip()
        user = storage.add_user(name)
        if user:
            current_user_id = user["id"]
            current_username = user["name"]
        return

    print(f"\n{CYAN}Select a user profile:{RESET}")
    for i, user in enumerate(users, start=1):
        print(f"{YELLOW}{i}. {user['name']}{RESET}")
    print(f"{YELLOW}{len(users) + 1}. Create new user{RESET}")

    while True:
        try:
            choice = int(input("Enter choice: "))
            if 1 <= choice <= len(users):
                selected = users[choice - 1]
                current_user_id = selected["id"]
                current_username = selected["name"]
                print(f"Welcome back, {current_username}! 🎬")
                return
            elif choice == len(users) + 1:
                name = input("Enter new user name: ").strip()
                user = storage.add_user(name)
                if user:
                    current_user_id = user["id"]
                    current_username = user["name"]
                return
            else:
                print(f"{RED}Invalid choice.{RESET}")
        except ValueError:
            print(f"{RED}Please enter a number.{RESET}")


# ---------- MENU ----------

def print_menu() -> None:
    """Displays the main menu options for the movie database."""
    print(f"\n{CYAN}*** {current_username}'s Movies Database ***{RESET}\n")
    print(f"{YELLOW}0. Exit{RESET}")
    print(f"{YELLOW}1. List movies{RESET}")
    print(f"{YELLOW}2. Add movie{RESET}")
    print(f"{YELLOW}3. Delete movie{RESET}")
    print(f"{YELLOW}4. Update movie{RESET}")
    print(f"{YELLOW}5. Stats{RESET}")
    print(f"{YELLOW}6. Random movie{RESET}")
    print(f"{YELLOW}7. Search movie{RESET}")
    print(f"{YELLOW}8. Movies sorted by rating{RESET}")
    print(f"{YELLOW}9. Movies in chronological order{RESET}")
    print(f"{YELLOW}10. Filter movies{RESET}")
    print(f"{YELLOW}11. Generate website{RESET}")
    print(f"{YELLOW}12. Switch user{RESET}")  # NEW


# ---------- INPUT HELPERS ----------

def prompt_non_empty_string(prompt_text: str) -> str:
    """Prompts the user for a non-empty string and returns it."""
    while True:
        user_value = input(prompt_text).strip()
        if user_value:
            return user_value
        print(f"{RED}Input cannot be empty. Please try again.{RESET}")


def prompt_float_in_range(prompt_text: str, min_value: float = 0.0, max_value: float = 10.0) -> float:
    """Prompts the user for a float within a given range."""
    while True:
        raw = input(prompt_text).strip()
        try:
            parsed = float(raw)
            if parsed < min_value or parsed > max_value:
                raise ValueError
            return parsed
        except ValueError:
            print(f"{RED}Please enter a number between {min_value} and {max_value}.{RESET}")


def prompt_int_year(prompt_text: str, min_year: int = 1888, max_year: int = 2100) -> int:
    """Prompts the user for a valid year between min_year and max_year."""
    while True:
        raw = input(prompt_text).strip()
        try:
            parsed = int(raw)
            if parsed < min_year or parsed > max_year:
                raise ValueError
            return parsed
        except ValueError:
            print(f"{RED}Please enter a valid year between {min_year} and {max_year}.{RESET}")


def prompt_optional_float(prompt_text: str) -> float | None:
    """Prompts the user for an optional float (empty input returns None)."""
    raw = input(prompt_text).strip()
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        print(f"{RED}Invalid number. Leaving it blank (no filter).{RESET}")
        return None


def prompt_optional_int(prompt_text: str) -> int | None:
    """Prompts the user for an optional integer (empty input returns None)."""
    raw = input(prompt_text).strip()
    if raw == "":
        return None
    try:
        return int(raw)
    except ValueError:
        print(f"{RED}Invalid integer. Leaving it blank (no filter).{RESET}")
        return None


# ---------- MOVIE ACTIONS ----------

def list_movies() -> None:
    """Lists all movies stored in the database for the current user."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print(f"{current_username}, your movie collection is empty.")
        return
    print(f"\n{len(movies)} movie(s) in total")
    for title, info in movies.items():
        print(f"{title} ({info.get('year', 'Unknown')}): {info.get('rating', 'N/A')}")


def add_movie() -> None:
    """
    Add a new movie into the database for the current user.
    - First tries to fetch details (year, rating, poster) from OMDb API.
    - Falls back to manual input if needed.
    """
    title = prompt_non_empty_string("Enter new movie title: ")

    from movie_api import fetch_movie
    year, rating, poster_url = fetch_movie(title)

    if year is None or rating is None or poster_url is None:
        print("Could not fetch complete data from OMDb API. Enter details manually.")
        year = prompt_int_year("Enter release year: ")
        rating = prompt_float_in_range("Enter rating (0-10): ")
        poster_url = input("Enter poster URL (or leave blank): ").strip() or None

    success = storage.add_movie(current_user_id, title, year, rating, poster_url)

    if success:
        print(f"{GREEN}Movie '{title}' added successfully.{RESET}")
    else:
        print(f"{RED}Could not add movie '{title}' (maybe already exists).{RESET}")


def delete_movie() -> None:
    """Prompts user for a title and deletes it from the current user's collection."""
    title = prompt_non_empty_string("Enter the title to delete: ")
    storage.delete_movie(current_user_id, title)


def update_movie() -> None:
    """Prompts user for a title and updates its rating (for the current user)."""
    title = prompt_non_empty_string("Enter the title to update: ")
    new_rating = prompt_float_in_range("Enter new rating (0-10): ")
    storage.update_movie(current_user_id, title, new_rating)


# ---------- STATS AND TOOLS ----------

def _compute_average_and_median(ratings: list[float]) -> tuple[float, float]:
    """Helper function: computes average and median from a list of ratings."""
    count = len(ratings)
    if count == 0:
        return (0.0, 0.0)
    average_value = sum(ratings) / count
    sorted_ratings = sorted(ratings)
    if count % 2 == 1:
        median_value = sorted_ratings[count // 2]
    else:
        left = sorted_ratings[count // 2 - 1]
        right = sorted_ratings[count // 2]
        median_value = (left + right) / 2.0
    return (average_value, median_value)


def print_statistics() -> None:
    """Prints average, median, best, and worst movie ratings for current user."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print("No movies found.")
        return
    ratings = [float(info.get("rating", 0.0)) for info in movies.values()]
    average_rating, median_rating = _compute_average_and_median(ratings)
    highest_rating = max(ratings)
    lowest_rating = min(ratings)
    best_titles = [t for t, i in movies.items() if float(i.get("rating", 0.0)) == highest_rating]
    worst_titles = [t for t, i in movies.items() if float(i.get("rating", 0.0)) == lowest_rating]
    print(f"\nAverage rating: {average_rating:.1f}")
    print(f"Median rating: {median_rating:.1f}")
    print(f"Best movie: {', '.join(best_titles)}, {highest_rating:.1f}")
    print(f"Worst movie: {', '.join(worst_titles)}, {lowest_rating:.1f}")


def random_movie() -> None:
    """Displays a random movie from the current user's database."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print("No movies found.")
        return
    random_title = random.choice(list(movies.keys()))
    info = movies[random_title]
    print(f"\n{random_title} ({info.get('year', 'Unknown')}): {info.get('rating', 'N/A')}")


def search_movie() -> None:
    """Searches for movies containing a given substring in the title (for current user)."""
    query = prompt_non_empty_string("Enter part of the movie title to search: ").lower()
    movies = storage.list_movies(current_user_id)
    matches = [f"{t} ({i.get('year','Unknown')}): {i.get('rating','N/A')}"
               for t, i in movies.items() if query in t.lower()]
    if matches:
        for line in matches:
            print(line)
    else:
        print("No matches found.")


def sort_movies_by_rating() -> None:
    """Sorts and displays movies by rating in descending order (current user only)."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print("No movies found.")
        return
    titles_sorted = sorted(movies.keys(), key=lambda t: float(movies[t].get("rating", 0.0)), reverse=True)
    for title in titles_sorted:
        info = movies[title]
        print(f"{title} ({info.get('year', 'Unknown')}): {info.get('rating', 'N/A')}")


def sort_movies_chronological() -> None:
    """Sorts and displays movies by release year (ascending or descending)."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print("No movies found.")
        return
    while True:
        user_choice = input("Show latest first? (y/n): ").strip().lower()
        if user_choice in {"y", "n"}:
            break
        print(f"{RED}Please enter 'y' or 'n'.{RESET}")
    reverse_order = True if user_choice == "y" else False
    titles_sorted = sorted(movies.keys(), key=lambda t: int(movies[t].get("year", 0)), reverse=reverse_order)
    for title in titles_sorted:
        info = movies[title]
        print(f"{title} ({info.get('year', 'Unknown')}): {info.get('rating', 'N/A')}")


def filter_movies() -> None:
    """Filters movies based on optional min rating, start year, and end year (for current user)."""
    movies = storage.list_movies(current_user_id)
    if not movies:
        print("No movies found.")
        return
    min_rating = prompt_optional_float("Enter minimum rating (leave blank for no minimum rating): ")
    start_year = prompt_optional_int("Enter start year (leave blank for no start year): ")
    end_year = prompt_optional_int("Enter end year (leave blank for no end year): ")

    filtered_lines = []
    for title, info in movies.items():
        rating_value = float(info.get("rating", 0.0))
        year_value = int(info.get("year", 0))
        if min_rating is not None and rating_value < min_rating:
            continue
        if start_year is not None and year_value < start_year:
            continue
        if end_year is not None and year_value > end_year:
            continue
        filtered_lines.append(f"{title} ({year_value}): {rating_value}")

    print("Filtered Movies:" if filtered_lines else "No movies match the filters.")
    for line in filtered_lines:
        print(line)


# ---------- MENU HANDLER ----------

def handle_menu_choice(user_choice: str) -> bool:
    """Executes the correct function based on the menu choice."""
    if user_choice == "0":
        print(f"{MAGENTA}Bye!{RESET}")
        return False
    elif user_choice == "1":
        list_movies()
    elif user_choice == "2":
        add_movie()
    elif user_choice == "3":
        delete_movie()
    elif user_choice == "4":
        update_movie()
    elif user_choice == "5":
        print_statistics()
    elif user_choice == "6":
        random_movie()
    elif user_choice == "7":
        search_movie()
    elif user_choice == "8":
        sort_movies_by_rating()
    elif user_choice == "9":
        sort_movies_chronological()
    elif user_choice == "10":
        filter_movies()
    elif user_choice == "11":
        website_generator.generate_website(current_user_id, current_username)
    elif user_choice == "12":
        select_user()  # NEW
    else:
        print(f"{RED}Invalid choice, please enter a number between 0 and 12.{RESET}")
    return True


# ---------- MAIN LOOP ----------

def main() -> None:
    """Main program loop: starts with user selection, shows menu, and handles input."""
    select_user()  # Always start by choosing a profile
    while True:
        print_menu()
        try:
            user_choice = input(f"{GREEN}Enter choice (0-12): {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{MAGENTA}Bye!{RESET}")
            break
        if not handle_menu_choice(user_choice):
            break


if __name__ == "__main__":
    main()
