import sqlite3

def reset_subjects():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # 1. Update status to available
    cursor.execute("""
        UPDATE subject 
        SET status='available' 
        WHERE department='CSE' AND year='2nd Year' AND semester='Semester 4'
    """)
    
    # 2. Delete assignments for these subjects
    cursor.execute("""
        DELETE FROM faculty_subject 
        WHERE subject_id IN (
            SELECT id FROM subject 
            WHERE department='CSE' AND year='2nd Year' AND semester='Semester 4'
        )
    """)
    
    conn.commit()
    count = cursor.rowcount
    conn.close()
    print(f"Successfully reset subjects for CSE 2nd Year Sem 4. {count} assignments cleared.")

if __name__ == "__main__":
    reset_subjects()
