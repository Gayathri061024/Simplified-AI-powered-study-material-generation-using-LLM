import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app, db, Faculty, Subject, FacultySubject
from flask import session
from datetime import datetime

def test_seniority_selection():
    with app.test_request_context():
        # Setup Test Data
        with app.app_context():
            # L3 Faculty (Should be open at 11 AM)
            fac3 = Faculty.query.filter_by(username="fac_l3").first()
            if not fac3:
                fac3 = Faculty(name="Fac L3", username="fac_l3", seniority_level=3, password="123")
                db.session.add(fac3)
            
            # L4 Faculty (Should be closed at 11 AM)
            fac4 = Faculty.query.filter_by(username="fac_l4").first()
            if not fac4:
                fac4 = Faculty(name="Fac L4", username="fac_l4", seniority_level=4, password="123")
                db.session.add(fac4)

            sub_avail = Subject.query.filter_by(subject_code="AVAIL101").first()
            if not sub_avail:
                sub_avail = Subject(course_level="UG", department="CSE", year="1st Year", semester="Semester 1", 
                                    subject_code="AVAIL101", subject_name="Available Sub", status="available")
                db.session.add(sub_avail)
            else:
                sub_avail.status = "available"
            db.session.commit()
            
            fac3_id = fac3.id
            fac4_id = fac4.id
            sub_avail_id = sub_avail.id
            
            print(f"L3 ID: {fac3_id}, L4 ID: {fac4_id}, Sub ID: {sub_avail_id}")

        # Test L3 Selection
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['faculty_logged_in'] = True
                sess['faculty_id'] = fac3_id
            
            # 1. Check if L3 can view available subjects
            with app.app_context():
                s = Subject.query.get(sub_avail_id)
                print(f"DEBUG: Subject {sub_avail_id} status in DB: {s.status}")
                all_avail = Subject.query.filter_by(status="available").all()
                print(f"DEBUG: All available subjects: {[sub.subject_code for sub in all_avail]}")

            response = client.get('/faculty/selection')
            print(f"DEBUG: now.hour={datetime.now().hour}")
            # print(f"DEBUG: Response data:\n{response.data.decode()[:1000]}") # Only first 1000 chars
            assert b"AVAIL101" in response.data
            print("[SUCCESS] L3 see available subjects.")
            assert b"Window Locked" not in response.data

            # 2. Check if L3 can confirm selection
            response = client.post('/faculty/confirm_selection', data={'subject_id': sub_avail_id}, follow_redirects=True)
            assert b"Successfully selected" in response.data
            
            # Refresh sub
            with app.app_context():
                s = Subject.query.get(sub_avail_id)
                assert s.status == "assigned"
            print("[SUCCESS] L3 successfully selected subject.")

        # Test L4 Selection
        # Reset sub to available for test
        with app.app_context():
            s = Subject.query.get(sub_avail_id)
            s.status = "available"
            db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['faculty_logged_in'] = True
                sess['faculty_id'] = fac4_id
            
            # 3. Check if L4 window is closed (assuming time is 11 AM)
            response = client.get('/faculty/selection')
            from flask import g
            print(f"DEBUG: now.hour={datetime.now().hour}, L4 start_hour={8+4}")
            # print(f"DEBUG: Response data contains 'Window Locked': {b'Window Locked' in response.data}")
            assert b"Window Locked" in response.data
            print("[SUCCESS] L4 window is locked.")

            # 4. Check if L4 selection attempt is blocked
            response = client.post('/faculty/confirm_selection', data={'subject_id': sub_avail_id}, follow_redirects=True)
            assert b"Your window is not open yet" in response.data
            print("[SUCCESS] L4 selection attempt blocked.")

if __name__ == "__main__":
    test_seniority_selection()
