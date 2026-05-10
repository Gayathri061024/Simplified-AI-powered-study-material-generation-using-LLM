import sqlite3

def migrate():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    print("Migrating Faculty table...")
    try:
        cursor.execute("ALTER TABLE faculty ADD COLUMN email VARCHAR(100)")
        print("Added email to faculty.")
    except sqlite3.OperationalError:
        print("Faculty email already exists.")

    print("Migrating StudyHistory table...")
    try:
        cursor.execute("ALTER TABLE study_history ADD COLUMN is_verified BOOLEAN DEFAULT 0")
        cursor.execute("ALTER TABLE study_history ADD COLUMN verified_by VARCHAR(100)")
        cursor.execute("ALTER TABLE study_history ADD COLUMN subject_id INTEGER REFERENCES subject(id)")
        print("Added verification columns to study_history.")
    except sqlite3.OperationalError as e:
        print(f"StudyHistory columns might already exist: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
