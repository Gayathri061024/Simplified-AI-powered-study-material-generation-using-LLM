from app import app, Subject

def simulate_broadcast():
    with app.app_context():
        dept = "CSE"
        year = "1st Year"
        sem = "Semester 1"
        subjects = Subject.query.filter_by(department=dept, year=year, semester=sem, status="available").all()
        print(f"Subjects for {dept} {year} {sem}:")
        for s in subjects:
            print(f"- {s.subject_code}: {s.subject_name}")

if __name__ == "__main__":
    simulate_broadcast()
