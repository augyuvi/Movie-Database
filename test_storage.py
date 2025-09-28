from storage.movie_storage_sql import add_movie, list_movies, delete_movie, update_movie, add_user, get_all_users

# Make sure we have a test user
user = add_user("TestUser")
if user is None:
    # If already exists, fetch it
    user = [u for u in get_all_users() if u["name"] == "TestUser"][0]
user_id = user["id"]

# Clean up if exists
delete_movie(user_id, "Inception")

print("\n-- Add --")
add_movie(user_id, "Inception", 2010, 8.8)

print("\n-- List --")
print(list_movies(user_id))

print("\n-- Update --")
update_movie(user_id, "Inception", 9.0)
print(list_movies(user_id))

print("\n-- Delete --")
delete_movie(user_id, "Inception")
print(list_movies(user_id))
