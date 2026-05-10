import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM subject WHERE department='CSE' AND year='1st Year' AND semester='Semester 1'")
for row in cursor.fetchall():
    print(row)
conn.close()
