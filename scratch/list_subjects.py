from app import app, Subject

def list_subjects():
    with app.app_context():
        subjects = Subject.query.filter_by(
            department="CSE",
            year="1st Year",
            semester="Semester 1"
        ).all()
        for s in subjects:
            print(f"Code: {s.subject_code}, Name: {s.subject_name}")

if __name__ == "__main__":
    list_subjects()
