# Step 4: Display scores
cursor.execute("SELECT username, reputation_score FROM users")
for username, score in cursor.fetchall():
    print(f"{username}: {score}")

@app.route("/profile/<int:user_id>")
def profile(user_id):
    cursor.execute("SELECT username, reputation_score FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    return f"<h2>{user[0]}</h2><p>Reputation Score: {user[1]}</p>"
