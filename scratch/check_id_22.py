from app import app, db, Subject

with app.app_context():
    s = db.session.get(Subject, 22)
    if s:
        print(f"Found Subject 22: {s.subject_code}, {s.subject_name}")
    else:
        print("Subject 22 not found.")
