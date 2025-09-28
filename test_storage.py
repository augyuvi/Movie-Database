from storage.movie_storage_sql import add_movie, list_movies, delete_movie, update_movie


# Clean up if exists
delete_movie("Inception")

print("\n-- Add --")
add_movie("Inception", 2010, 8.8)

print("\n-- List --")
print(list_movies())

print("\n-- Update --")
update_movie("Inception", 9.0)
print(list_movies())

print("\n-- Delete --")
delete_movie("Inception")
print(list_movies())
