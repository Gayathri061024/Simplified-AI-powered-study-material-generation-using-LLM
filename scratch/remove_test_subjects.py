from app import app, db, Subject

def remove_test_subjects():
    with app.app_context():
        subjects_to_remove = ["TEST102", "AVAIL101", "BROAD101"]
        for code in subjects_to_remove:
            subject = Subject.query.filter_by(subject_code=code).first()
            if subject:
                db.session.delete(subject)
                print(f"Deleted subject: {code}")
            else:
                print(f"Subject not found: {code}")
        db.session.commit()
        print("Done.")

if __name__ == "__main__":
    remove_test_subjects()
