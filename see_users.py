import sqlite3

conn = sqlite3.connect("dev.db")
cur = conn.cursor()

cur.execute("SELECT id, full_name, email, phone, created_at FROM users ORDER BY id DESC;")
rows = cur.fetchall()

for r in rows:
    print(r)

conn.close()
