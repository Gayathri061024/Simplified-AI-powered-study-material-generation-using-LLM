from app import app, db, Student

with app.app_context():
    # Set all existing students to verified
    count = Student.query.update({Student.is_verified: True})
    db.session.commit()
    print(f"[SUCCESS]: Verified {count} existing students!")
