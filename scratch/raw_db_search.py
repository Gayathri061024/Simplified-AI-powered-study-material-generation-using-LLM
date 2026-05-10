import os

with open('students.db', 'rb') as f:
    data = f.read()
    
terms = [b"TEST102", b"AVAIL101", b"BROAD101"]
for term in terms:
    pos = data.find(term)
    if pos != -1:
        print(f"Found {term} at position {pos}")
        # Print some surrounding data
        start = max(0, pos - 50)
        end = min(len(data), pos + 100)
        print(f"  Surrounding data: {data[start:end]}")
    else:
        print(f"{term} not found in file.")
