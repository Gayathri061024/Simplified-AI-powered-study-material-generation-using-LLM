import sqlite3
from werkzeug.security import generate_password_hash

def reset_password():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    username = "faculty2"
    new_password = "faculty123"
    hashed_password = generate_password_hash(new_password)
    
    print(f"Attempting to reset password for {username}...")
    
    cursor.execute("SELECT id FROM faculty WHERE username = ?", (username,))
    f_id = cursor.fetchone()
    
    if f_id:
        cursor.execute("UPDATE faculty SET password = ? WHERE username = ?", (hashed_password, username))
        conn.commit()
        print(f"✅ Success! User '{username}' password reset to '{new_password}'.")
    else:
        print(f"❌ Error: User '{username}' not found in database.")
        
    conn.close()

if __name__ == "__main__":
    reset_password()
