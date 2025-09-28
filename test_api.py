# ---------------------------------------------------------
# test_api.py
# Tester for movie_api.py (Movie Project)
# Verifies that OMDb API fetching works correctly
# ---------------------------------------------------------

import movie_api

print("Fetching Titanic...")
year, rating, poster_url = movie_api.fetch_movie("Titanic")
print("Year:", year, "Rating:", rating, "Poster:", poster_url)
