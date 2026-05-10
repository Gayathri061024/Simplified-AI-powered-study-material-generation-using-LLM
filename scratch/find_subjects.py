from app import app, Subject

def find_subjects():
    with app.app_context():
        codes = ["TEST102", "AVAIL101", "BROAD101"]
        for code in codes:
            subjects = Subject.query.filter_by(subject_code=code).all()
            if subjects:
                for s in subjects:
                    print(f"Code: {s.subject_code}, Name: {s.subject_name}, Dept: {s.department}, Year: {s.year}, Sem: {s.semester}")
            else:
                print(f"Code {code} not found anywhere.")

if __name__ == "__main__":
    find_subjects()
