# website_generator.py
import storage.movie_storage_sql as storage


def generate_website(user_id, username):
    """Generate index.html (or username.html) using the movies stored for a user."""
    movies = storage.list_movies(user_id)

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
                <p>Rating: {info.get("rating", "N/A")}</p>
            </div>
        </li>
        """

    # Replace placeholders in the template
    final_html = template.replace("__TEMPLATE_TITLE__", f"{username}'s Movie App")
    final_html = final_html.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)

    # Save website as <username>.html inside _static
    output_file = f"_static/{username}.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"Website for {username} was generated successfully → {output_file}")
