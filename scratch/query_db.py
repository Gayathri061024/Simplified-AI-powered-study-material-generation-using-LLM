import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'students.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM subject")
rows = cursor.fetchall()

print(f"Total subjects in DB: {len(rows)}")
for row in rows:
    print(row)

conn.close()
