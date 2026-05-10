import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app, db, Subject, FacultySubject

def sync_status():
    with app.app_context():
        # Reset all to available first (to handle any removals)
        db.session.query(Subject).update({Subject.status: "available"})
        
        # Mark assigned ones
        assigned_subject_ids = [fs.subject_id for fs in FacultySubject.query.all()]
        if assigned_subject_ids:
            num_updated = db.session.query(Subject).filter(Subject.id.in_(assigned_subject_ids)).update({Subject.status: "assigned"}, synchronize_session=False)
            print(f"Updated {num_updated} subjects to 'assigned'.")
        
        db.session.commit()
        print("Sync complete.")

if __name__ == "__main__":
    sync_status()
