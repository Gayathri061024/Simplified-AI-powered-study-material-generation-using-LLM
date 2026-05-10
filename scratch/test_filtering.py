import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app, db, Student, Faculty, Subject, FacultySubject
from flask import session

def test_admin_get_subjects_filtering():
    with app.test_request_context():
        # Create a test faculty and subject
        with app.app_context():
            faculty = Faculty.query.filter_by(username="test_fac").first()
            if not faculty:
                faculty = Faculty(name="Test Faculty", username="test_fac", password="123")
                db.session.add(faculty)
            
            sub1 = Subject.query.filter_by(subject_code="TEST101").first()
            if not sub1:
                sub1 = Subject(course_level="UG", department="CSE", year="1st Year", semester="Semester 1", subject_code="TEST101", subject_name="Test Sub 1")
                db.session.add(sub1)
            
            sub2 = Subject.query.filter_by(subject_code="TEST102").first()
            if not sub2:
                sub2 = Subject(course_level="UG", department="CSE", year="1st Year", semester="Semester 1", subject_code="TEST102", subject_name="Test Sub 2")
                db.session.add(sub2)
            
            db.session.commit()
            
            # Assign sub1 to faculty
            assign = FacultySubject.query.filter_by(faculty_id=faculty.id, subject_id=sub1.id).first()
            if not assign:
                assign = FacultySubject(faculty_id=faculty.id, subject_id=sub1.id)
                db.session.add(assign)
            db.session.commit()

            print(f"Faculty ID: {faculty.id}")
            print(f"Sub1 ID: {sub1.id}, Sub2 ID: {sub2.id}")

        # Simulate Faculty Session
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['faculty_logged_in'] = True
                sess['faculty_id'] = faculty.id
                sess['admin_logged_in'] = False
            
            response = client.post('/admin/get_subjects', data={
                'course_level': 'UG',
                'department': 'CSE',
                'year': '1st Year',
                'semester': 'Semester 1'
            })
            data = response.get_json()
            print(f"Faculty Response: {data}")
            codes = [s['code'] for s in data]
            assert "TEST101" in codes
            assert "TEST102" not in codes
            print("[SUCCESS] Faculty filtering works!")

        # Simulate Admin Session
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['admin_logged_in'] = True
                sess['faculty_logged_in'] = False
            
            response = client.post('/admin/get_subjects', data={
                'course_level': 'UG',
                'department': 'CSE',
                'year': '1st Year',
                'semester': 'Semester 1'
            })
            data = response.get_json()
            print(f"Admin Response: {data}")
            codes = [s['code'] for s in data]
            assert "TEST101" in codes
            assert "TEST102" in codes
            print("[SUCCESS] Admin sees all subjects!")

            # Test hide_assigned
            response = client.post('/admin/get_subjects', data={
                'course_level': 'UG',
                'department': 'CSE',
                'year': '1st Year',
                'semester': 'Semester 1',
                'hide_assigned': 'true'
            })
            data = response.get_json()
            print(f"Admin (hide_assigned) Response: {data}")
            codes = [s['code'] for s in data]
            assert "TEST101" not in codes
            assert "TEST102" in codes
            print("[SUCCESS] Admin hide_assigned works!")

if __name__ == "__main__":
    test_admin_get_subjects_filtering()
