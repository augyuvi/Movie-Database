# ---------------------------------------------------------
# movie_api.py
# Handles communication with the OMDb API for Movie Project
# ---------------------------------------------------------

import requests

# This is the OMDb API key for this project
API_KEY = "4134f61f"  # replace with your own key if needed
BASE_URL = "http://www.omdbapi.com/"


def fetch_movie(title: str):
    """
    Fetches movie details (year, rating, poster_url) from OMDb API.
    Returns (year, rating, poster_url) or (None, None, None) on failure.
    """
    try:
        response = requests.get(BASE_URL, params={"apikey": API_KEY, "t": title})
        data = response.json()

        # Check if movie was found
        if data.get("Response") == "False":
            print(f"Error: {data.get('Error', 'Movie not found')}")
            return None, None, None

        year = int(data.get("Year", 0)) if data.get("Year") else None
        rating = float(data.get("imdbRating", 0)) if data.get("imdbRating") != "N/A" else None
        poster_url = data.get("Poster", None) if data.get("Poster") != "N/A" else None

        return year, rating, poster_url

    except requests.exceptions.RequestException as e:
        print(f"Network error while accessing OMDb API: {e}")
        return None, None, None
