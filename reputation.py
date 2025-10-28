import sqlite3

conn = sqlite3.connect("database.sqlite")
cursor = conn.cursor()

def calculate_reputation(user_id):
    cursor.execute("SELECT SUM(likes*2) FROM posts WHERE user_id=?", (user_id,))
    post_points = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(likes) FROM comments WHERE user_id=?", (user_id,))
    comment_points = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*)*5 FROM reports WHERE reported_user_id=?", (user_id,))
    report_points = cursor.fetchone()[0] or 0

    total_score = post_points + comment_points - report_points

    cursor.execute("UPDATE users SET reputation_score=? WHERE id=?", (total_score, user_id))
    conn.commit()

cursor.execute("SELECT id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

for uid in user_ids:
    calculate_reputation(uid)

print("Reputation updated for all users.")

