import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'students.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find all subjects with code containing TEST, AVAIL, or BROAD
cursor.execute("SELECT id, subject_code, subject_name FROM subject WHERE subject_code LIKE '%TEST%' OR subject_code LIKE '%AVAIL%' OR subject_code LIKE '%BROAD%'")
rows = cursor.fetchall()

if not rows:
    print("No subjects found matching the criteria.")
else:
    print(f"Found {len(rows)} subjects to delete:")
    for row in rows:
        print(row)
        cursor.execute("DELETE FROM subject WHERE id=?", (row[0],))
        print(f"Deleted ID {row[0]}")

conn.commit()
conn.close()
print("Done.")
