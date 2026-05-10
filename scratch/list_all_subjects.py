from app import app, Subject

def list_all():
    with app.app_context():
        subjects = Subject.query.all()
        for s in subjects:
            print(f"ID: {s.id}, Code: {s.subject_code}, Name: {s.subject_name}, Dept: {s.department}, Year: {s.year}, Sem: {s.semester}, Status: {s.status}")

if __name__ == "__main__":
    list_all()
