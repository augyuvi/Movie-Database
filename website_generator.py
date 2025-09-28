# website_generator.py
import movie_storage_sql as storage

def generate_website():
    """Generate index.html using the movies stored in the database."""
    movies = storage.list_movies()

    # Read the template file
    with open("_static/index_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    # Build the movie grid HTML
    movie_grid_html = ""
    for title, info in movies.items():
        year = info.get("year", "Unknown")
        poster_url = info.get("poster_url")

        # Fallback if no poster from API
        if not poster_url or poster_url == "None":
            poster_url = "https://via.placeholder.com/128x193.png?text=No+Image"

        movie_grid_html += f"""
        <li>
            <div class="movie">
                <img src="{poster_url}" alt="{title} poster" class="movie-poster">
                <div class="movie-title">{title}</div>
                <div class="movie-year">{year}</div>
            </div>
        </li>
        """

    # Replace placeholders in the template
    final_html = template.replace("__TEMPLATE_TITLE__", "Masterschool's Movie App")
    final_html = final_html.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)

    # Write index.html inside _static
    with open("_static/index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

    print("Website was generated successfully.")
