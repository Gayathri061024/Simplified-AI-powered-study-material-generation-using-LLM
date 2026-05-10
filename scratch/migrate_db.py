import sqlite3
import os

db_path = 'students.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE student ADD COLUMN semester VARCHAR(20) DEFAULT 'Semester 1'")
        print("Success: Added semester column to student table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Notice: Semester column already exists.")
        else:
            print(f"Error: {e}")
    conn.commit()
    conn.close()
else:
    print("Notice: students.db not found. It will be created by app.py automatically.")
