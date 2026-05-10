import sqlite3
import os

# Get path to the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# The db path as used in app.py: os.path.join(BASE_DIR, 'students.db')
# But wait, scratch is a subdirectory, so we go up one.
DB_PATH = os.path.join(BASE_DIR, "..", "students.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Checking Faculty table...")
    try:
        cursor.execute("ALTER TABLE faculty ADD COLUMN seniority_level INTEGER DEFAULT 1")
        print("Added seniority_level to Faculty.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("seniority_level already exists in Faculty.")
        else:
            print(f"Error adding seniority_level: {e}")

    print("Checking Subject table...")
    try:
        cursor.execute("ALTER TABLE subject ADD COLUMN status VARCHAR(20) DEFAULT 'available'")
        print("Added status to Subject.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("status already exists in Subject.")
        else:
            print(f"Error adding status: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
