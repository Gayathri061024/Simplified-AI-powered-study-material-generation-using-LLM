import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), 'students.db')

print(f"Connecting to database at {DB_PATH}...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    print("Adding 'language_preference' column to 'study_history'...")
    cursor.execute("ALTER TABLE study_history ADD COLUMN language_preference VARCHAR(20) DEFAULT 'english'")
    print("Successfully added 'language_preference'.")
except sqlite3.OperationalError as e:
    print(f"Info: {e}")

try:
    print("Adding 'generation_mode' column to 'study_history'...")
    cursor.execute("ALTER TABLE study_history ADD COLUMN generation_mode VARCHAR(20) DEFAULT 'detailed'")
    print("Successfully added 'generation_mode'.")
except sqlite3.OperationalError as e:
    print(f"Info: {e}")

conn.commit()
conn.close()
print("Migration complete!")
