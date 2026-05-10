import sqlite3

conn = sqlite3.connect('students.db')
cur = conn.cursor()

# Update 1st year CSE faculty with NULL semester -> Semester 1
cur.execute(
    "UPDATE faculty SET semester = ? WHERE department = ? AND year = ? AND semester IS NULL",
    ("Semester 1", "CSE", "1st Year")
)
print(f"Updated {cur.rowcount} faculty record(s)")
conn.commit()

# Verify all faculty
cur.execute("SELECT id, name, department, year, semester, seniority_level FROM faculty")
print("\nAll faculty after fix:")
for r in cur.fetchall():
    print(r)

conn.close()
