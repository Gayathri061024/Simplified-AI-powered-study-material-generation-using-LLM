import sqlite3

def find_in_all_tables():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    search_terms = ["TEST102", "AVAIL101", "BROAD101"]
    
    for table in tables:
        print(f"Searching in table: {table}")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [c[1] for c in cursor.fetchall()]
        
        for column in columns:
            for term in search_terms:
                query = f"SELECT * FROM {table} WHERE {column} LIKE ?"
                cursor.execute(query, (f'%{term}%',))
                results = cursor.fetchall()
                if results:
                    print(f"  MATCH in column '{column}':")
                    for row in results:
                        print(f"    {row}")
    
    conn.close()

if __name__ == "__main__":
    find_in_all_tables()
