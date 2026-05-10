import sqlite3
import os

def update_emails():
    # Detect the database path correctly
    db_path = 'students.db'
    if not os.path.exists(db_path):
        print(f"❌ Error: Database '{db_path}' not found in current directory.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the test email from the user's config (or use a default)
    test_email = "purnima.g.in@gmail.com" # Default test email
    
    print(f"Updating all faculty to use: {test_email}")
    
    try:
        cursor.execute("UPDATE faculty SET email = ?", (test_email,))
        conn.commit()
        count = cursor.rowcount
        print(f"✅ Successfully updated {count} faculty members.")
    except Exception as e:
        print(f"❌ Error during update: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_emails()
