from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from generator import generate_study_material, extract_text_from_pdf, generate_blooms, generate_important_questions
from pdf_export import generate_pdf
from plagiarism import check_plagiarism
from materials import get_subjects, get_material_path, list_material_files, get_next_index
from urllib.parse import unquote, quote
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- SMTP Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
MAIL_USERNAME = "example1@gmail.com"
MAIL_PASSWORD = "xxxx xxxx xxxx"
SENDER_NAME = "StudyAI Admin"

def send_smtp_email(to_email, subject, body):
    """Sends an actual email using Flask-Mail."""
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body,
            sender=f"{SENDER_NAME} <{MAIL_USERNAME}>"
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return False
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import os
import markdown as md
import sqlite3
import threading
import secrets
import string

app = Flask(__name__)

# --- Mail Configuration -------------------------------------------------------
app.config['MAIL_SERVER'] = SMTP_SERVER
app.config['MAIL_PORT'] = SMTP_PORT
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = f"{SENDER_NAME} <{MAIL_USERNAME}>"

mail = Mail(app)

@app.template_filter('markdown')
def markdown_filter(text):
    if not text:
        return ""
    import re
    # Process [QUESTION] tags before markdown conversion
    text = re.sub(r'\[QUESTION\](.*?)\[QUESTION\]', r'<div class="highlight-question">\1</div>', text, flags=re.DOTALL)
    return md.markdown(text, extensions=['extra'])

app.secret_key = "studyapp_secret_key_2024"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'students.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = os.path.join(BASE_DIR, "study_materials")
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# --- Models -------------------------------------------------------------------

class Student(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(100), unique=True, nullable=False)
    roll_no    = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    year       = db.Column(db.String(20), nullable=False)
    semester   = db.Column(db.String(20), nullable=False, default="Semester 1")
    password   = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    # --- New Fields for OTP Verification ---
    is_verified      = db.Column(db.Boolean, default=False)
    verification_otp = db.Column(db.String(10))

class Admin(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Faculty(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(100))
    department = db.Column(db.String(50))
    year       = db.Column(db.String(20))
    semester   = db.Column(db.String(20)) # New field for granular filtering
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    last_login = db.Column(db.DateTime)
    seniority_level = db.Column(db.Integer, default=1) # New Level Field
    needs_password_change = db.Column(db.Boolean, default=True)

class FacultySubject(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    
    faculty = db.relationship("Faculty", backref="assigned_subjects")
    subject = db.relationship("Subject", backref="assigned_faculty")

class StudyHistory(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    student_id          = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    department          = db.Column(db.String(50))
    year                = db.Column(db.String(20))
    semester            = db.Column(db.String(20))
    subject             = db.Column(db.String(100))
    topic               = db.Column(db.String(100))
    summary             = db.Column(db.Text)
    short_notes         = db.Column(db.Text)
    coding_examples     = db.Column(db.Text)
    important_questions = db.Column(db.Text)
    mcqs                = db.Column(db.Text)
    pyq                 = db.Column(db.Text)
    blooms_remember     = db.Column(db.Text)
    blooms_understand   = db.Column(db.Text)
    blooms_apply        = db.Column(db.Text)
    blooms_analyze      = db.Column(db.Text)
    blooms_evaluate     = db.Column(db.Text)
    blooms_create       = db.Column(db.Text)
    youtube_links       = db.Column(db.Text)
    pdf_path            = db.Column(db.String(200))
    course_level        = db.Column(db.String(10))
    
    # --- Updated Verification Status System ---
    is_verified         = db.Column(db.Boolean, default=False) # Legacy compatibility
    status              = db.Column(db.String(20), default="pending") # pending, verified, rejected
    rejection_reason    = db.Column(db.Text)
    verified_by         = db.Column(db.String(100))
    view_count          = db.Column(db.Integer, default=0)
    language_preference = db.Column(db.String(20), default="english")
    generation_mode     = db.Column(db.String(20), default="detailed")
    subject_id          = db.Column(db.Integer, db.ForeignKey("subject.id"))
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="history", lazy=True)
    subj = db.relationship("Subject", backref="history")

class SelectionWindow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(50))
    year = db.Column(db.String(20))
    semester = db.Column(db.String(20))
    broadcast_at = db.Column(db.DateTime, default=datetime.now)

class NoteRating(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey("study_history.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    rating     = db.Column(db.Integer, nullable=False) # 1-5
    comment    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    history = db.relationship("StudyHistory", backref="ratings")
    student_relationship = db.relationship("Student", backref="ratings_given")

class Subject(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    course_level = db.Column(db.String(10), nullable=False, default="UG") # Added Course Level (UG/PG)
    department   = db.Column(db.String(50), nullable=False)
    year         = db.Column(db.String(20), nullable=False)
    semester     = db.Column(db.String(20), nullable=False)
    subject_code = db.Column(db.String(20), nullable=False)
    subject_name = db.Column(db.String(200), nullable=False)
    status       = db.Column(db.String(20), default="available") # New status Field

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Student, int(user_id))

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

def faculty_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("faculty_logged_in"):
            return redirect(url_for("faculty_login"))
        
        # Forced password change check
        faculty = db.session.get(Faculty, session.get("faculty_id"))
        if faculty and faculty.needs_password_change and request.endpoint != 'faculty_change_password':
            flash("You must change your password before proceeding.")
            return redirect(url_for("faculty_change_password"))
            
        return f(*args, **kwargs)
    return decorated

def staff_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in") and not session.get("faculty_logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def any_user_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not (current_user.is_authenticated or session.get("admin_logged_in") or session.get("faculty_logged_in")):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username="admin").first():
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created - username: admin | password: admin123")
    else:
        print("Admin already exists in database")

    if not Faculty.query.filter_by(username="faculty").first():
        fac = Faculty(
            name="Default Faculty",
            username="faculty",
            password=generate_password_hash("faculty123")
        )
        db.session.add(fac)
        db.session.commit()
        print("Default faculty created - username: faculty | password: faculty123")
    else:
        print("Faculty already exists in database")
        
    # Sync subjects from SUBJECTS dict — adds any new ones missing in DB
    from materials import SUBJECTS
    added = 0
    for dept, years in SUBJECTS.items():
        for year, semesters in years.items():
            for semester, subjects in semesters.items():
                for subj in subjects:
                    exists = Subject.query.filter_by(
                        course_level="UG", department=dept, year=year,
                        semester=semester, subject_code=subj["code"]
                    ).first()
                    if not exists:
                        db.session.add(Subject(
                            course_level="UG",
                            department=dept, year=year,
                            semester=semester,
                            subject_code=subj["code"],
                            subject_name=subj["name"]
                        ))
                        added += 1
    if added:
        db.session.commit()
        print(f"✅ Added {added} new subject(s) to database")

def send_verification_alert(faculty_list, subject, topic):
    """Sends background email alerts to assigned faculty."""
    if not faculty_list:
        return
        
    with app.app_context():
        for faculty in faculty_list:
            if not faculty.email:
                continue
            try:
                msg = Message(
                    subject=f"ACTION REQUIRED: AI Material Pending Review - {topic}",
                    recipients=[faculty.email],
                    body=f"Hello {faculty.name},\n\n"
                         f"New AI-generated study material for your subject '{subject}' on the topic '{topic}' is pending your verification.\n\n"
                         f"Please log in to the Faculty Portal to review and approve the content.\n\n"
                         f"Best regards,\nStudy Material Team"
                )
                mail.send(msg)
            except Exception as e:
                print(f"Error sending email to {faculty.email}: {e}")

# ─── Verification Management ──────────────────────────────────────────────────
@app.route("/faculty/verify")
@faculty_required
def faculty_verify_queue():
    faculty = db.session.get(Faculty, session["faculty_id"])
    assigned_subject_ids = [fs.subject_id for fs in faculty.assigned_subjects]
    
    pending_items = StudyHistory.query.filter(
        StudyHistory.subject_id.in_(assigned_subject_ids),
        StudyHistory.status == "pending"
    ).order_by(StudyHistory.created_at.desc()).all()
    
    # Calculate stats for display
    total_verified = StudyHistory.query.filter(
        StudyHistory.subject_id.in_(assigned_subject_ids),
        StudyHistory.status == "verified"
    ).count()

    return render_template("faculty_verify.html", 
                           pending_items=pending_items,
                           stats_verified=total_verified)

@app.route("/faculty/approve/<int:item_id>")
@faculty_required
def faculty_approve_item(item_id):
    item = db.get_or_404(StudyHistory, item_id)
    faculty = db.session.get(Faculty, session["faculty_id"])
    
    # Security check: Is this faculty assigned to this subject?
    assigned_ids = [fs.subject_id for fs in faculty.assigned_subjects]
    if item.subject_id not in assigned_ids:
        flash("Unauthorized verification attempt.")
        return redirect(url_for("faculty_verify_queue"))
        
    item.status = "verified"
    item.is_verified = True # Legacy support
    item.rejection_reason = None
    item.verified_by = faculty.name
    db.session.commit()
    flash(f"✅ Verified: {item.topic}")
    return redirect(url_for("faculty_verify_queue"))

@app.route("/faculty/reject/<int:item_id>", methods=["POST"])
@faculty_required
def faculty_reject_item(item_id):
    item = db.get_or_404(StudyHistory, item_id)
    faculty = db.session.get(Faculty, session["faculty_id"])
    
    # Security check
    assigned_ids = [fs.subject_id for fs in faculty.assigned_subjects]
    if item.subject_id not in assigned_ids:
        flash("Unauthorized rejection attempt.")
        return redirect(url_for("faculty_verify_queue"))
        
    reason = request.form.get("reason")
    if not reason:
        flash("⚠️ Rejection reason is mandatory.")
        return redirect(url_for("faculty_verify_queue"))

    # Implement Regenerate on Reject Logic
    item.status = "pending" # Back to pending
    item.is_verified = False
    item.rejection_reason = reason
    item.verified_by = faculty.name
    db.session.commit()
    
    # Trigger AI Regeneration in Background
    import threading
    threading.Thread(target=execute_generation_process, args=(item.id,)).start()
    
    flash(f"❌ Feedback sent. AI is now regenerating '{item.topic}' based on your rejection.")
    return redirect(url_for("faculty_verify_queue"))

@app.route("/faculty/edit/<int:item_id>", methods=["GET", "POST"])
@faculty_required
def faculty_edit_item(item_id):
    item = db.get_or_404(StudyHistory, item_id)
    faculty = db.session.get(Faculty, session["faculty_id"])
    
    # Security check
    assigned_ids = [fs.subject_id for fs in faculty.assigned_subjects]
    if item.subject_id not in assigned_ids:
        flash("Unauthorized edit attempt.")
        return redirect(url_for("faculty_verify_queue"))
        
    if request.method == "POST":
        item.summary = request.form.get("summary")
        item.short_notes = request.form.get("short_notes")
        item.coding_examples = request.form.get("coding_examples")
        item.important_questions = request.form.get("important_questions")
        item.mcqs = request.form.get("mcqs")
        
        item.is_verified = True
        item.verified_by = faculty.name
        db.session.commit()
        flash(f"Updated and Verified: {item.topic}")
        return redirect(url_for("faculty_verify_queue"))
        
    return render_template("faculty_edit.html", item=item)

# ─── Student Routes ───────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("std_uid")
        password = request.form.get("std_pwd")
        student  = Student.query.filter_by(email=email).first()
        if student and check_password_hash(student.password, password):
            student.last_login = datetime.utcnow()
            db.session.commit()
            login_user(student)
            return redirect(url_for("dashboard"))
        flash("Invalid email or password!")
    
    # Fetch all registered student emails for suggestions
    students = Student.query.all()
    student_emails = [s.email for s in students]
    return render_template("login.html", student_emails=student_emails)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name       = request.form.get("name")
        email      = request.form.get("email")
        roll_no    = request.form.get("roll_no")
        department = request.form.get("department", "")
        year       = request.form.get("year", "")
        semester   = request.form.get("semester", "")
        password   = request.form.get("password")

        if Student.query.filter_by(email=email).first():
            flash("Email already registered!")
            return render_template("register.html")
        if Student.query.filter_by(roll_no=roll_no).first():
            flash("Roll number already registered!")
            return render_template("register.html")

        hashed = generate_password_hash(password)
        student = Student(name=name, email=email, roll_no=roll_no,
                          department=department, year=year, semester=semester,
                          password=hashed, verification_otp=None, is_verified=True)
        db.session.add(student)
        db.session.commit()
        
        flash("Registration successful! You can now login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")
    return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_verified:
        logout_user()
        flash("Please verify your email first.")
        return redirect(url_for("login"))
    
    # Recommended topics: Top 5 verified items in student's department by view_count
    recommendations = StudyHistory.query.filter_by(
        department=current_user.department,
        status="verified"
    ).order_by(StudyHistory.view_count.desc()).limit(5).all()
    
    return render_template("dashboard.html", student=current_user, recommendations=recommendations)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/get_subjects", methods=["POST"])
@login_required
def fetch_subjects():
    course_level = request.form.get("course_level", "UG")
    department   = request.form.get("department")
    year         = request.form.get("year")
    semester     = request.form.get("semester")
    
    subjects = Subject.query.filter_by(
        course_level=course_level,
        department=department,
        year=year,
        semester=semester
    ).order_by(Subject.subject_code).all()
    
    return jsonify([{"code": s.subject_code, "name": s.subject_name} for s in subjects])

@app.route("/get_material_files", methods=["POST"])
@login_required
def get_material_files():
    """Student-facing API: returns list of uploaded files for a given subject + type."""
    from materials import list_material_files
    course_level = request.form.get("course_level", "UG")
    department   = request.form.get("department")
    regulation   = request.form.get("regulation", "R2021")
    year         = request.form.get("year")
    semester     = request.form.get("semester")
    subject_code = request.form.get("subject_code")
    file_type    = request.form.get("file_type")
    files = list_material_files(department, course_level, regulation, year, semester, subject_code, file_type)
    result = [{"index": f["index"]} for f in files]
    return jsonify({"files": result})

# --- Shared Material Routes ---
def get_path_parts(encoded_path):
    parts = encoded_path.split("/")
    if len(parts) >= 6:
        department, course_level, regulation, year, semester, subject_code = [unquote(p) for p in parts[:6]]
        index = int(parts[6]) if len(parts) >= 7 else 1
        return department, course_level, regulation, year, semester, subject_code, index
    elif len(parts) == 5:
        department, regulation, year, semester, subject_code = [unquote(p) for p in parts[:5]]
        return department, "UG", regulation, year, semester, subject_code, 1
    return None

def handle_material_view(encoded_path, file_type):
    parts = get_path_parts(encoded_path)
    if not parts: return ("Invalid path", 404) if request.method == "GET" else ("", 404)
    dept, level, reg, yr, sem, code, idx = parts
    files = list_material_files(dept, level, reg, yr, sem, code, file_type)
    match = next((f for f in files if f["index"] == idx), files[0] if files else None)
    if match and os.path.exists(match["path"]):
        return send_file(match["path"], mimetype="application/pdf") if request.method == "GET" else ("", 200)
    return (f"No {file_type.replace('_',' ')} available.", 404) if request.method == "GET" else ("", 404)

def handle_material_download(encoded_path, file_type):
    parts = get_path_parts(encoded_path)
    if not parts: return "Invalid path", 404
    dept, level, reg, yr, sem, code, idx = parts
    files = list_material_files(dept, level, reg, yr, sem, code, file_type)
    match = next((f for f in files if f["index"] == idx), files[0] if files else None)
    if match and os.path.exists(match["path"]):
        return send_file(match["path"], mimetype="application/pdf", as_attachment=True, download_name=f"{code}_{file_type.upper()}_{idx}.pdf")
    return f"No {file_type.replace('_',' ')} available.", 404

@app.route("/view_notes/<path:encoded_path>", methods=["GET", "HEAD"])
@any_user_required
def view_notes(encoded_path): return handle_material_view(encoded_path, "notes")

@app.route("/download_notes/<path:encoded_path>")
@any_user_required
def download_notes(encoded_path): return handle_material_download(encoded_path, "notes")

@app.route("/view_pyq/<path:encoded_path>", methods=["GET", "HEAD"])
@any_user_required
def view_pyq(encoded_path): return handle_material_view(encoded_path, "pyq")

@app.route("/download_pyq/<path:encoded_path>")
@any_user_required
def download_pyq(encoded_path): return handle_material_download(encoded_path, "pyq")

@app.route("/view_syllabus/<path:encoded_path>", methods=["GET", "HEAD"])
@any_user_required
def view_syllabus(encoded_path): return handle_material_view(encoded_path, "syllabus")

@app.route("/download_syllabus/<path:encoded_path>")
@any_user_required
def download_syllabus(encoded_path): return handle_material_download(encoded_path, "syllabus")

@app.route("/view_question_bank/<path:encoded_path>", methods=["GET", "HEAD"])
@any_user_required
def view_question_bank(encoded_path): return handle_material_view(encoded_path, "question_bank")

@app.route("/download_question_bank/<path:encoded_path>")
@any_user_required
def download_question_bank(encoded_path): return handle_material_download(encoded_path, "question_bank")

def get_file_list_urls(department, course_level, regulation, year, semester, subject_code, file_type):
    from materials import list_material_files
    raw = list_material_files(department, course_level, regulation, year, semester, subject_code, file_type)
    file_prefix = "view_question_bank" if file_type == "question_bank" else f"view_{file_type}"
    base = f"/{file_prefix}/{quote(department)}/{quote(course_level)}/{quote(regulation)}/{quote(year)}/{quote(semester)}/{quote(subject_code)}"
    return [{"index": f["index"], "url": f"{base}/{f['index']}"} for f in raw]

@app.route("/student/list_files", methods=["POST"])
@login_required
def student_list_files():
    course_level = request.form.get("course_level", "UG")
    department   = request.form.get("department")
    regulation   = request.form.get("regulation", "R2021")
    year         = request.form.get("year")
    semester     = request.form.get("semester")
    subject_code = request.form.get("subject_code")
    file_type    = request.form.get("file_type")
    
    from materials import list_material_files
    files = list_material_files(department, course_level, regulation, year, semester, subject_code, file_type)
    result = []
    for f in files:
        # Use relative path for downloads
        rel_path = os.path.relpath(f["path"], BASE_DIR)
        result.append({"index": f["index"], "name": f"{file_type}_{f['index']}.pdf", "path": rel_path})
    return jsonify({"files": result})

def execute_generation_process(record_id):
    """Core logic to (re)generate AI content and PDF for a StudyHistory record."""
    with app.app_context():
        history = db.session.get(StudyHistory, record_id)
        if not history: return
        
        # Pull metadata
        subject = history.subject
        topic   = history.topic
        mode    = history.generation_mode
        lang_pref = history.language_preference
        
        # Get PDF context if available
        sc = subject.split(" - ")[0]
        notes_path = get_material_path(history.department, history.course_level, "R2021", history.year, history.semester, sc, "notes")
        pdf_text = extract_text_from_pdf(notes_path) if notes_path else None
        
        try:
            import time
            sections = generate_study_material(subject, topic, pdf_text, lang_pref, mode)
            
            time.sleep(2)
            sections["important_questions"] = generate_important_questions(subject, topic, lang_pref, mode)
            time.sleep(2)
            blooms = generate_blooms(subject, topic, lang_pref, mode)
            output_pdf = generate_pdf(subject, topic, sections)
            
            # Update record
            history.summary = sections.get("summary", "")
            history.short_notes = sections.get("short_notes", "")
            history.coding_examples = sections.get("coding_examples", "")
            history.important_questions = sections.get("important_questions", "")
            history.mcqs = sections.get("mcqs", "")
            history.pyq = sections.get("previous_year_questions", "")
            history.blooms_remember     = blooms.get("remember", "")
            history.blooms_understand   = blooms.get("understand", "")
            history.blooms_apply        = blooms.get("apply", "")
            history.blooms_analyze      = blooms.get("analyze", "")
            history.blooms_evaluate     = blooms.get("evaluate", "")
            history.blooms_create       = blooms.get("create", "")
            history.youtube_links       = sections.get("youtube_links", "")
            history.pdf_path            = output_pdf
            history.status              = "pending"
            history.is_verified         = False
            
            db.session.commit()
            
            subject_record = history.subj
            if subject_record:
                assigned_faculty = [fs.faculty for fs in subject_record.assigned_faculty]
                if assigned_faculty:
                    send_verification_alert(assigned_faculty, subject, topic)
                    
            return True
        except Exception as e:
            print(f"Generation error for record {record_id}: {e}")
            return False

@app.route("/generate", methods=["POST"])
@login_required
def generate():
    course_level  = request.form.get("course_level", "UG")
    department   = request.form.get("department")
    year         = request.form.get("year")
    semester     = request.form.get("semester")
    regulation   = request.form.get("regulation", "R2021")
    subject_code = request.form.get("subject_code")
    subject_name = request.form.get("subject_name")
    topic        = request.form.get("topic")
    mode        = "detailed" # Default for now as user removed field
    lang_pref    = request.form.get("language_preference", "english")
    subject      = f"{subject_code} - {subject_name}"

    subject_record = Subject.query.filter_by(
        department=department,
        year=year,
        semester=semester,
        subject_code=subject_code,
        subject_name=subject_name
    ).first()
    force = request.form.get("force") == "true"

    # Check for existing verified content first
    existing = StudyHistory.query.filter_by(
        subject_id=subject_record.id if subject_record else None,
        topic=topic,
        status="verified"
    ).first()
    
    if existing and not force:
        flash("Returning existing verified content for this topic.")
        return redirect(url_for("view_history", record_id=existing.id))

    # Create record initial state
    history = StudyHistory(
        student_id=current_user.id, course_level=course_level, department=department, year=year,
        semester=semester, subject=subject, subject_id=subject_record.id if subject_record else None,
        topic=topic, status="pending", is_verified=False,
        language_preference=lang_pref, generation_mode=mode
    )
    db.session.add(history)
    db.session.commit()

    # Run generation synchronously for the first-time student request
    success = execute_generation_process(history.id)
    
    if success:
        return redirect(url_for("view_history", record_id=history.id))
    else:
        db.session.delete(history)
        db.session.commit()
        flash("⚠️ AI Generation failed. Please try again.")
        return redirect(url_for("dashboard"))

@app.route("/submit_rating", methods=["POST"])
@login_required
def submit_rating():
    history_id = request.form.get("history_id")
    rating     = request.form.get("rating")
    comment    = request.form.get("comment", "")
    
    if not history_id or not rating:
        return jsonify({"success": False, "error": "Missing data"})
        
    # Check if user already rated
    existing = NoteRating.query.filter_by(history_id=history_id, student_id=current_user.id).first()
    if existing:
        existing.rating = int(rating)
        existing.comment = comment
    else:
        new_rating = NoteRating(history_id=history_id, student_id=current_user.id, rating=int(rating), comment=comment)
        db.session.add(new_rating)
        
    db.session.commit()
    return jsonify({"success": True, "msg": "Thank you for your feedback!"})

@app.route("/history")
@login_required
def history():
    # Show both verified and pending topics in the student vault
    records = StudyHistory.query.filter_by(
        student_id=current_user.id
    ).order_by(StudyHistory.created_at.desc()).all()
    return render_template("history.html", student=current_user, records=records)

@app.route("/history/<int:record_id>")
def view_history(record_id):
    record = db.get_or_404(StudyHistory, record_id)
    
    # Increment View Count
    record.view_count += 1
    db.session.commit()
    
    # Permission Check
    is_authorized = False
    viewer_name = "Guest"
    
    if current_user.is_authenticated:
        if record.student_id == current_user.id:
            is_authorized = True
            viewer_name = current_user.name
        elif record.status == "verified":
            is_authorized = True
            viewer_name = current_user.name
    elif session.get("faculty_id"):
        faculty = db.session.get(Faculty, session["faculty_id"])
        assigned_ids = [fs.subject_id for fs in faculty.assigned_subjects]
        if record.subject_id in assigned_ids:
            is_authorized = True
            viewer_name = faculty.name

    if not is_authorized:
        flash("🔒 This material is currently pending faculty verification. Please check back later!")
        return redirect(url_for("dashboard"))

    # Prepare data for template
    sc = record.subject.split(" - ")[0]
    pyq_files      = get_file_list_urls(record.department, record.course_level or "UG", "R2021", record.year, record.semester, sc, "pyq")
    syllabus_files = get_file_list_urls(record.department, record.course_level or "UG", "R2021", record.year, record.semester, sc, "syllabus")
    qb_files       = get_file_list_urls(record.department, record.course_level or "UG", "R2021", record.year, record.semester, sc, "question_bank")
    notes_files    = get_file_list_urls(record.department, record.course_level or "UG", "R2021", record.year, record.semester, sc, "notes")

    sections = {
        "summary": record.summary, "short_notes": record.short_notes,
        "coding_examples": record.coding_examples,
        "important_questions": record.important_questions,
        "mcqs": record.mcqs, "previous_year_questions": record.pyq,
        "youtube_links": record.youtube_links
    }
    blooms = {
        "remember": record.blooms_remember or "", "understand": record.blooms_understand or "",
        "apply": record.blooms_apply or "", "analyze": record.blooms_analyze or "",
        "evaluate": record.blooms_evaluate or "", "create": record.blooms_create or ""
    }
    return render_template("result.html",
        student=viewer_name, course_level=record.course_level or "UG", department=record.department, year=record.year,
        semester=record.semester, regulation="R2021", subject=record.subject,
        subject_code=sc, topic=record.topic,
        sections=sections, blooms=blooms, pdf_path=record.pdf_path,
        pyq_available=len(pyq_files) > 0, pyq_files=pyq_files,
        syllabus_available=len(syllabus_files) > 0, syllabus_files=syllabus_files,
        qb_available=len(qb_files) > 0, qb_files=qb_files,
        notes_available=len(notes_files) > 0, notes_files=notes_files,
        is_verified=record.is_verified, status=record.status, verified_by=record.verified_by,
        rejection_reason=record.rejection_reason,
        record_id=record.id,
        current_rating=NoteRating.query.filter_by(history_id=record.id, student_id=current_user.id).first() if current_user.is_authenticated else None,
        all_ratings=record.ratings)

@app.route("/history/delete/<int:record_id>")
@login_required
def delete_history(record_id):
    record = db.get_or_404(StudyHistory, record_id)
    if record.student_id != current_user.id:
        flash("Unauthorized.")
        return redirect(url_for("history"))
    db.session.delete(record)
    db.session.commit()
    flash("Record deleted.")
    return redirect(url_for("history"))

@app.route("/download/<path:filename>")
@login_required
def download(filename):
    return send_file(filename, as_attachment=True)

# --- Faculty Routes -------------------------------------------------------------

@app.route("/faculty/login", methods=["GET", "POST"])
def faculty_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        faculty = Faculty.query.filter_by(username=username).first()
        if faculty and check_password_hash(faculty.password, password):
            faculty.last_login = datetime.utcnow()
            db.session.commit()
            session["faculty_logged_in"] = True
            session["faculty_id"] = faculty.id
            session["faculty_username"] = username
            
            if faculty.needs_password_change:
                flash("Welcome! Please set a new password for your account.")
                return redirect(url_for("faculty_change_password"))
                
            return redirect(url_for("faculty_dashboard"))
        flash("Invalid faculty credentials!")
    return render_template("faculty_login.html")

@app.route("/faculty/change-password", methods=["GET", "POST"])
def faculty_change_password():
    if not session.get("faculty_logged_in"):
        return redirect(url_for("faculty_login"))
        
    if request.method == "POST":
        new_pw = request.form.get("new_password")
        confirm_pw = request.form.get("confirm_password")
        
        if not new_pw or len(new_pw) < 6:
            flash("Password must be at least 6 characters long.")
        elif new_pw != confirm_pw:
            flash("Passwords do not match!")
        else:
            faculty = db.session.get(Faculty, session.get("faculty_id"))
            faculty.password = generate_password_hash(new_pw)
            faculty.needs_password_change = False
            db.session.commit()
            flash("Password updated successfully! Welcome to your dashboard.")
            return redirect(url_for("faculty_dashboard"))
            
    return render_template("faculty_change_password.html")

@app.route("/faculty/logout")
def faculty_logout():
    session.pop("faculty_logged_in", None)
    session.pop("faculty_id", None)
    session.pop("faculty_username", None)
    return redirect(url_for("faculty_login"))

@app.route("/faculty")
@faculty_required
def faculty_dashboard():
    from materials import list_all_subjects
    faculty_id = session.get("faculty_id")
    faculty = db.session.get(Faculty, faculty_id) # Fetch full details
    
    assigned_records = FacultySubject.query.filter_by(faculty_id=faculty_id).all()
    assigned_subject_ids = [r.subject_id for r in assigned_records]
    
    # Filter all subjects to show only assigned ones
    all_subs = list_all_subjects()
    assigned_subjects = [s for s in all_subs if s["id"] in assigned_subject_ids]
    
    # Calculate pending verification tasks
    pending_count = StudyHistory.query.filter(
        StudyHistory.subject_id.in_(assigned_subject_ids),
        StudyHistory.is_verified == False
    ).count()
    
    return render_template("faculty_dashboard.html", 
                         faculty=faculty,
                         assigned_subjects=assigned_subjects,
                         faculty_name=faculty.name if faculty else "Faculty",
                         pending_count=pending_count)

def _is_window_open_for(faculty):
    """
    Seniority-based check (no timer).
    - Requires a broadcast to exist for this cohort.
    - L1 can select immediately after broadcast.
    - L(N) can select only after ALL faculty at L(N-1) … L1 have selected.
    Returns (is_open: bool, waiting_for_level: int|None)
    """
    window = SelectionWindow.query.filter_by(
        department=faculty.department,
        year=faculty.year,
        semester=faculty.semester
    ).order_by(SelectionWindow.broadcast_at.desc()).first()

    if not window:
        return False, None  # No broadcast yet

    if faculty.seniority_level == 1:
        return True, None   # Highest priority – always open after broadcast

    # Check every seniority level that is senior to this faculty
    higher_faculty = Faculty.query.filter(
        Faculty.department == faculty.department,
        Faculty.year == faculty.year,
        Faculty.semester == faculty.semester,
        Faculty.seniority_level < faculty.seniority_level
    ).all()

    if not higher_faculty:
        return True, None   # No one senior in this cohort

    unselected = [
        f for f in higher_faculty
        if not FacultySubject.query.filter_by(faculty_id=f.id).first()
    ]

    if not unselected:
        return True, None   # All seniors have chosen

    # Find the most-senior level still pending (lowest number = highest seniority)
    waiting_for = min(f.seniority_level for f in unselected)
    return False, waiting_for


def notify_next_seniority_level(faculty_id, dept, year, semester):
    """
    Background task: after a faculty selects, if ALL faculty at that level
    have now selected, email the immediate next level with what was chosen
    and which subjects remain.
    """
    with app.app_context():
        faculty = db.session.get(Faculty, faculty_id)
        if not faculty:
            return

        current_level = faculty.seniority_level

        # Have ALL at this level now selected?
        same_level = Faculty.query.filter_by(
            department=dept, year=year, semester=semester,
            seniority_level=current_level
        ).all()

        all_done = all(
            FacultySubject.query.filter_by(faculty_id=f.id).first()
            for f in same_level
        )
        if not all_done:
            return  # Still waiting for peers

        next_level = current_level + 1
        next_faculty = Faculty.query.filter_by(
            department=dept, year=year, semester=semester,
            seniority_level=next_level
        ).all()
        if not next_faculty:
            return  # No next level

        # Build summary of what current level chose
        chosen_lines = []
        for f in same_level:
            fs = FacultySubject.query.filter_by(faculty_id=f.id).first()
            if fs:
                chosen_lines.append(
                    f"  • {f.name} (L{current_level}) → "
                    f"{fs.subject.subject_code}: {fs.subject.subject_name}"
                )
        chosen_str = "\n".join(chosen_lines) or "  (none)"

        # Remaining available subjects
        remaining = Subject.query.filter_by(
            department=dept, year=year, semester=semester, status="available"
        ).all()
        remaining_str = (
            "\n".join(f"  - {s.subject_code}: {s.subject_name}" for s in remaining)
            if remaining else "  No subjects remaining."
        )

        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_logs.txt")

        for f in next_faculty:
            if not f.email:
                continue
            subj_line = f"Your Turn: Subject Selection Open – {dept} {year} {semester}"
            body = (
                f"Dear {f.name},\n\n"
                f"Level {current_level} faculty have completed their subject selections:\n"
                f"{chosen_str}\n\n"
                f"It is now your turn (Priority Level {next_level}) to select your subject.\n\n"
                f"Remaining Available Subjects:\n{remaining_str}\n\n"
                f"Please log in to make your selection:\n"
                f"http://127.0.0.1:5000/faculty/selection\n\n"
                f"Regards,\nAdmin Team"
            )
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(f"\n--- NEXT-LEVEL NOTIFY {datetime.now()} ---\n")
                log.write(f"TO: {f.email}\nBODY:\n{body}\n{'─'*30}\n")
            send_smtp_email(f.email, subj_line, body)


@app.route("/faculty/selection")
@faculty_required
def faculty_selection():
    faculty = db.session.get(Faculty, session["faculty_id"])
    is_window_open, waiting_for_level = _is_window_open_for(faculty)

    broadcast_exists = SelectionWindow.query.filter_by(
        department=faculty.department,
        year=faculty.year,
        semester=faculty.semester
    ).first() is not None

    all_subjects = Subject.query.filter_by(
        department=faculty.department,
        year=faculty.year,
        semester=faculty.semester
    ).all()

    my_assignment = FacultySubject.query.filter_by(faculty_id=faculty.id).first()

    return render_template("faculty_selection.html",
                           faculty=faculty,
                           all_subjects=all_subjects,
                           is_window_open=is_window_open,
                           broadcast_exists=broadcast_exists,
                           waiting_for_level=waiting_for_level,
                           my_assignment=my_assignment)


@app.route("/faculty/confirm_selection", methods=["POST"])
@faculty_required
def faculty_confirm_selection():
    faculty = db.session.get(Faculty, session["faculty_id"])

    is_open, _ = _is_window_open_for(faculty)
    if not is_open:
        flash("⚠️ Your selection window is not open yet. Please wait for senior staff to complete their selection.")
        return redirect(url_for("faculty_selection"))

    # Enforce one subject per staff
    existing = FacultySubject.query.filter_by(faculty_id=faculty.id).first()
    if existing:
        flash("⚠️ You have already selected a subject. Only one subject is allowed per staff member.")
        return redirect(url_for("faculty_dashboard"))

    subject_id = request.form.get("subject_id")
    subject = db.get_or_404(Subject, subject_id)

    if subject.status != "available":
        flash("⚠️ This subject has already been claimed by another staff member.")
        return redirect(url_for("faculty_selection"))

    # Create assignment
    assignment = FacultySubject(faculty_id=faculty.id, subject_id=subject.id)
    subject.status = "assigned"
    db.session.add(assignment)
    db.session.commit()

    flash(f"✅ Successfully selected: {subject.subject_code} – {subject.subject_name}")

    # Notify next seniority level in background
    threading.Thread(
        target=notify_next_seniority_level,
        args=(faculty.id, faculty.department, faculty.year, faculty.semester),
        daemon=True
    ).start()

    return redirect(url_for("faculty_dashboard"))

# --- Admin Routes ---------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"Admin login attempt -> username: {username}")
        admin = Admin.query.filter_by(username=username).first()
        print(f"Admin found: {admin}")
        if admin and check_password_hash(admin.password, password):
            session["admin_logged_in"] = True
            session["admin_username"]  = username
            print("[SUCCESS] Admin login successful")
            return redirect(url_for("admin_dashboard"))
        print("[ERROR] Admin login failed")
        flash("Invalid admin credentials!")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    from sqlalchemy import func
    from materials import list_all_subjects

    total_students    = Student.query.count()
    total_faculty     = Faculty.query.count()
    total_generations = StudyHistory.query.count()
    today             = datetime.utcnow().date()
    
    # Logins today
    student_logins_today = Student.query.filter(db.func.date(Student.last_login) == today).count()
    faculty_logins_today = Faculty.query.filter(db.func.date(Faculty.last_login) == today).count()
    today_generations = StudyHistory.query.filter(
        db.func.date(StudyHistory.created_at) == today).count()

    # [STATS] Most studied subjects
    top_subjects = db.session.query(
        StudyHistory.subject,
        func.count(StudyHistory.id).label("count")
    ).group_by(StudyHistory.subject)\
     .order_by(func.count(StudyHistory.id).desc())\
     .limit(5).all()

    print(f"Top subjects: {top_subjects}")  # Debug

    recent_history = StudyHistory.query.order_by(
        StudyHistory.created_at.desc()).limit(10).all()

    all_subjects = list_all_subjects()

    # NEW: Chart stats
    total_verified = StudyHistory.query.filter_by(status="verified").count()
    total_pending = StudyHistory.query.filter_by(status="pending").count()
    total_rejected = StudyHistory.query.filter_by(status="rejected").count()

    return render_template("admin_dashboard.html",
        total_students=total_students,
        total_faculty=total_faculty,
        student_logins_today=student_logins_today,
        faculty_logins_today=faculty_logins_today,
        total_generations=total_generations,
        today_generations=today_generations,
        top_subjects=top_subjects,
        recent_history=recent_history,
        all_subjects=all_subjects,
        stats_verified=total_verified,
        stats_pending=total_pending,
        stats_rejected=total_rejected
    )

@app.route("/admin/students")
@admin_required
def admin_students():
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template("admin_students.html", students=students)

@app.route("/admin/history")
@admin_required
def admin_history():
    records = StudyHistory.query.order_by(StudyHistory.created_at.desc()).all()
    return render_template("admin_history.html", records=records)

@app.route("/admin/students/delete/<int:student_id>")
@admin_required
def admin_delete_student(student_id):
    student = db.get_or_404(Student, student_id)
    StudyHistory.query.filter_by(student_id=student_id).delete()
    db.session.delete(student)
    db.session.commit()
    flash(f"Student {student.name} deleted successfully.")
    return redirect(url_for("admin_students"))

@app.route("/admin/upload", methods=["GET", "POST"])
@app.route("/admin/upload/<file_type>", methods=["POST"])
@staff_required
def admin_upload(file_type=None):
    is_faculty = session.get("faculty_logged_in")
    return_url = url_for("admin_upload")

    if request.method == "POST":
        course_level = request.form.get("course_level", "UG")
        department   = request.form.get("department")
        regulation   = request.form.get("regulation", "R2021")
        year         = request.form.get("year")
        semester     = request.form.get("semester")
        subject_code = request.form.get("subject_code")
        file_type    = file_type or request.form.get("file_type")
        files        = request.files.getlist("pdf_file")

        # --- Faculty Security Check ---
        if is_faculty:
            faculty_id = session.get("faculty_id")
            allowed = FacultySubject.query.join(Subject).filter(
                FacultySubject.faculty_id == faculty_id,
                Subject.subject_code == subject_code,
                Subject.department == department,
                Subject.year == year,
                Subject.semester == semester
            ).first()
            if not allowed:
                flash("[ERROR] Unauthorized: You are not assigned to this subject.")
                return redirect(return_url)

        if not files or not any(f.filename for f in files):
            flash("Please select at least one PDF file.")
            return redirect(url_for("admin_upload"))

        uploaded = 0
        for file in files:
            if not file or not file.filename.endswith(".pdf"):
                continue
            idx = get_next_index(department, course_level, regulation, year, semester, subject_code, file_type)
            folder = os.path.join(UPLOAD_FOLDER, department, course_level, regulation, year, semester, subject_code)
            os.makedirs(folder, exist_ok=True)
            filepath = os.path.join(folder, f"{file_type}_{idx}.pdf")
            file.save(filepath)
            uploaded += 1

        if uploaded:
            flash(f"[SUCCESS] {uploaded} file(s) uploaded successfully for {subject_code} ({file_type})!")
        else:
            flash("Please upload valid PDF file(s).")
        return redirect(url_for("admin_upload", active_tab=file_type))

    # For GET request, if faculty, provide their single assigned subject
    assigned_subject = None
    if is_faculty:
        faculty_id = session.get("faculty_id")
        assigned_subject = Subject.query.join(FacultySubject).filter(FacultySubject.faculty_id == faculty_id).first()

    active_tab = request.args.get("active_tab", "notes")
    if active_tab == "question_bank": active_tab = "qb"
    return render_template("admin_upload.html", assigned_subject=assigned_subject, active_tab=active_tab)


@app.route("/admin/delete_material", methods=["POST"])
@app.route("/admin/delete_material/<file_type>/<path:rest>", methods=["POST"])
@staff_required
def admin_delete_material(file_type=None, rest=None):
    if rest:
        parts = rest.split("/")
        if len(parts) >= 7:
            department, course_level, regulation, year, semester, subject_code, index = [unquote(p) for p in parts[:7]]
        elif len(parts) == 6:
            department, regulation, year, semester, subject_code, index = [unquote(p) for p in parts[:6]]
            course_level = "UG"
        elif len(parts) == 5:
            # Fallback for old sessions without regulation in path
            department, year, semester, subject_code, index = [unquote(p) for p in parts[:5]]
            course_level, regulation = "UG", "R2021" # Defaults
        else:
            flash("Invalid delete URL.")
            return redirect(url_for("admin_upload") if session.get("admin_logged_in") else url_for("faculty_dashboard"))
    else:
        course_level = request.form.get("course_level", "UG")
        department   = request.form.get("department")
        regulation   = request.form.get("regulation", "R2021")
        year         = request.form.get("year")
        semester     = request.form.get("semester")
        subject_code = request.form.get("subject_code")
        file_type    = file_type or request.form.get("file_type")
        index        = request.form.get("index")

    folder   = os.path.join(UPLOAD_FOLDER, department, course_level, regulation, year, semester, subject_code)
    filepath = os.path.join(folder, f"{file_type}_{index}.pdf")
    if os.path.exists(filepath):
        os.remove(filepath)
        
        # Re-index remaining files sequentially
        prefix = f"{file_type}_"
        remaining_files = []
        for fname in os.listdir(folder):
            if fname.startswith(prefix) and fname.endswith(".pdf"):
                try:
                    idx = int(fname[len(prefix):-4])
                    remaining_files.append((idx, fname))
                except ValueError:
                    pass
        
        remaining_files.sort(key=lambda x: x[0])
        
        for new_idx, (old_idx, fname) in enumerate(remaining_files, start=1):
            if new_idx != old_idx:
                old_path = os.path.join(folder, fname)
                new_path = os.path.join(folder, f"{file_type}_{new_idx}.pdf")
                os.rename(old_path, new_path)
                
        flash(f"[DELETED] {file_type}_{index}.pdf deleted and remaining files reindexed for {subject_code}.")
    else:
        flash("File not found.")
    return redirect(url_for("admin_upload"))

@app.route("/admin/get_subjects", methods=["POST"])
@staff_required
def admin_get_subjects():
    course_level  = request.form.get("course_level", "UG").strip()
    department    = request.form.get("department", "").strip()
    year          = request.form.get("year", "").strip()
    semester      = request.form.get("semester", "").strip()
    
    print(f"--- FETCH DEBUG ---")
    print(f"LEVEL: '{course_level}'")
    print(f"DEPT:  '{department}'")
    print(f"YEAR:  '{year}'")
    print(f"SEM:   '{semester}'")
    print(f"-------------------")
    
    # Init query
    query = Subject.query.filter_by(
        course_level=course_level,
        department=department,
        year=year,
        semester=semester
    )

    is_admin_session = session.get("admin_logged_in") == True
    is_faculty_session = session.get("faculty_logged_in") == True
    faculty_id_session = session.get("faculty_id")
    
    # Priority: If it's a faculty session, only show their subjects
    # UNLESS they are also an admin (unlikely, but we check admin_logged_in first)
    if is_faculty_session and faculty_id_session and not is_admin_session:
        assigned_ids = [fs.subject_id for fs in FacultySubject.query.filter_by(faculty_id=faculty_id_session).all()]
        if assigned_ids:
            query = query.filter(Subject.id.in_(assigned_ids))
        else:
            return jsonify([])
    
    # If it's an Admin session (and not handled by faculty logic above)
    elif is_admin_session:
        # Policy: Hide subjects already assigned to ANYONE to ensure unique assignments when managing faculty
        # This is used for the "Assign Faculty" page
        all_assigned_ids = [fs.subject_id for fs in FacultySubject.query.all()]
        if all_assigned_ids:
            # We only apply this "hide assigned" if it's the admin_faculty page.
            # However, for the admin_upload page, they might want to see EVERYTHING.
            # To distinguish, we look at the origin or just skip this filter for now as it's confusing.
            # For now, let's keep it but only if "hide_assigned" is passed.
            if request.form.get("hide_assigned") == "true":
                query = query.filter(~Subject.id.in_(all_assigned_ids))
    
    final_subjects = query.order_by(Subject.subject_code).all()
    return jsonify([{"id": s.id, "code": s.subject_code, "name": s.subject_name} for s in final_subjects])

@app.route("/admin/add_subject", methods=["POST"])
@admin_required
def admin_add_subject():
    course_level = request.form.get("course_level", "UG")
    department   = request.form.get("department")
    year         = request.form.get("year")
    semester     = request.form.get("semester")
    subject_code = request.form.get("subject_code")
    subject_name = request.form.get("subject_name")

    if not all([course_level, department, year, semester, subject_code, subject_name]):
        flash("All fields are required to add a subject.")
        return redirect(url_for("admin_dashboard"))

    # Check if subject code already exists for that sem
    existing = Subject.query.filter_by(course_level=course_level, department=department, year=year, semester=semester, subject_code=subject_code).first()
    if existing:
        flash(f"Subject {subject_code} already exists in {semester}.")
        return redirect(url_for("admin_dashboard"))

    new_sub = Subject(
        course_level=course_level,
        department=department,
        year=year,
        semester=semester,
        subject_code=subject_code,
        subject_name=subject_name
    )
    db.session.add(new_sub)
    db.session.commit()
    flash(f"[SUCCESS] Added {subject_code} - {subject_name} to {department} {semester}.")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete_subject/<int:subject_id>")
@admin_required
def admin_delete_subject(subject_id):
    subject = db.get_or_404(Subject, subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash(f"Deleted subject: {subject.subject_code}")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/list_files", methods=["POST"])
@admin_required
def admin_list_files():
    course_level = request.form.get("course_level", "UG")
    department   = request.form.get("department")
    regulation   = request.form.get("regulation", "R2021")
    year         = request.form.get("year")
    semester     = request.form.get("semester")
    subject_code = request.form.get("subject_code")
    file_type    = request.form.get("file_type")
    
    from materials import list_material_files
    files = list_material_files(department, course_level, regulation, year, semester, subject_code, file_type)
    result = []
    for f in files:
        size_bytes = os.path.getsize(f["path"])
        size_str   = f"{size_bytes // 1024} KB" if size_bytes < 1024*1024 else f"{size_bytes / (1024*1024):.1f} MB"
        result.append({"index": f["index"], "name": f"{file_type}_{f['index']}.pdf", "size": size_str})
    return jsonify({"files": result})


@app.route("/admin/faculty")
@admin_required
def admin_faculty():
    all_faculty = Faculty.query.all()
    all_subjects = Subject.query.order_by(Subject.department, Subject.subject_code).all()
    return render_template("admin_faculty.html", faculty_list=all_faculty, subjects=all_subjects)


@app.route("/admin/notify_staff", methods=["POST"])
@admin_required
def admin_notify_staff():
    dept = request.form.get("department")
    year = request.form.get("year")
    sem  = request.form.get("semester")
    
    # 1. Fetch relevant faculty — must match department, year AND semester
    faculty_list = Faculty.query.filter_by(department=dept, year=year, semester=sem).all()
    if not faculty_list:
        flash(f"[INFO] No staff found for {dept} {year} {sem}. Please check faculty profiles.")
        return redirect(url_for("admin_faculty"))
    
    # 2. Fetch subjects for the email
    subjects = Subject.query.filter_by(department=dept, year=year, semester=sem, status="available").all()
    if not subjects:
        flash(f"[INFO] No available (unassigned) subjects found for {dept} {year} {sem}.")
        return redirect(url_for("admin_faculty"))

    # 2.5 Record broadcast time for the 2-minute staggered window
    new_window = SelectionWindow(department=dept, year=year, semester=sem, broadcast_at=datetime.now())
    db.session.add(new_window)
    db.session.commit()

    subject_list_str = "\n".join([f"- {s.subject_code}: {s.subject_name}" for s in subjects])
    
    # 3. Simulate sending emails
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_logs.txt")
    sent_count = 0
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n--- BROADCAST {datetime.now()} ---\n")
        f.write(f"Context: {dept} | {year} | {sem}\n")
        
        for faculty in faculty_list:
            if not faculty.email: continue
            
            subject = f"Subject Selection Open: {dept} {year} {sem}"
            email_body = f"""
Dear {faculty.name},

The subject selection window for {dept} {year} {sem} is now open.
Priority is based on your seniority level (L{faculty.seniority_level}).

Available Subjects:
{subject_list_str}

Please log in to your dashboard to make your selection:
http://127.0.0.1:5000/faculty/selection

Regards,
Admin Team
"""
            # 1. MOCK SEND: Log to file
            f.write(f"TO: {faculty.email}\n")
            f.write(f"BODY:\n{email_body}\n")
            f.write("-" * 30 + "\n")
            
            # 2. REAL SEND: Use SMTP (Refactored to Flask-Mail)
            success = send_smtp_email(faculty.email, subject, email_body)
            if success:
                sent_count += 1
            
    if sent_count > 0:
        flash(f"✨ [SUCCESS] Broadcasted notification to {sent_count} staff member(s). Details logged to email_logs.txt.")
    else:
        flash("⚠️ No notifications were sent. Please check if faculty have valid email addresses and SMTP credentials are correct.")
    return redirect(url_for("admin_faculty"))

@app.route("/admin/assign_faculty", methods=["POST"])
@admin_required
def admin_assign_faculty():
    faculty_name = request.form.get("faculty_name")
    faculty_email = request.form.get("faculty_email")
    
    if not faculty_name:
        flash("[ERROR] Faculty name is required.")
        return redirect(url_for("admin_faculty"))

    # Find or Create Faculty
    faculty = Faculty.query.filter_by(name=faculty_name).first()
    seniority = int(request.form.get("seniority_level", 1))

    if not faculty:
        # Generate Username
        username = "".join(e for e in faculty_name.lower() if e.isalnum())
        base_username = username
        counter = 1
        while Faculty.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Generate Random Password
        alphabet = string.ascii_letters + string.digits
        raw_password = ''.join(secrets.choice(alphabet) for i in range(10))
        
        faculty = Faculty(
            name=faculty_name,
            username=username,
            email=faculty_email,
            department=request.form.get("department_faculty"),
            year=request.form.get("year_faculty"),
            semester=request.form.get("semester_faculty"),
            seniority_level=seniority,
            password=generate_password_hash(raw_password),
            needs_password_change=True
        )
        db.session.add(faculty)
        db.session.commit()
        
        # Send Email with Credentials
        if faculty_email:
            try:
                msg = Message(
                    subject="Your Faculty Account Credentials",
                    recipients=[faculty_email],
                    body=f"Hello {faculty_name},\n\n"
                         f"Your account has been created on the StudyAI Platform.\n\n"
                         f"Username: {username}\n"
                         f"Initial Password: {raw_password}\n\n"
                         f"Please log in here: {url_for('faculty_login', _external=True)}\n"
                         f"Note: You will be required to change your password on your first login.\n\n"
                         f"Best regards,\nAdmin Team"
                )
                mail.send(msg)
                flash(f"[SUCCESS] Created account for {faculty_name}. Credentials sent to {faculty_email}.")
            except Exception as e:
                flash(f"[WARNING] Account created, but failed to send email: {e}")
        else:
            flash(f"[SUCCESS] Created account for {faculty_name}. No email provided for credentials.")
    else:
        # Update details
        if faculty_email: faculty.email = faculty_email
        faculty.seniority_level = seniority
        dept_fac = request.form.get("department_faculty")
        year_fac = request.form.get("year_faculty")
        sem_fac  = request.form.get("semester_faculty")
        if dept_fac: faculty.department = dept_fac
        if year_fac: faculty.year = year_fac
        if sem_fac:  faculty.semester = sem_fac
        db.session.commit()
        flash(f"[SUCCESS] Updated account for {faculty_name} (Seniority: L{seniority})")
        
    return redirect(url_for("admin_faculty"))

@app.route("/admin/delete_assignment/<int:assignment_id>")
@admin_required
def admin_delete_assignment(assignment_id):
    assignment = db.get_or_404(FacultySubject, assignment_id)
    # Reset the subject status back to "available" so it can be re-selected
    subject = db.session.get(Subject, assignment.subject_id)
    if subject:
        subject.status = "available"
    db.session.delete(assignment)
    db.session.commit()
    flash(f"✅ Assignment removed. '{subject.subject_code}' is now available for selection again.")
    return redirect(url_for("admin_faculty"))

@app.route("/admin/delete_faculty/<int:faculty_id>")
@admin_required
def admin_delete_faculty(faculty_id):
    faculty = db.get_or_404(Faculty, faculty_id)
    name = faculty.name
    # Delete assignments first
    FacultySubject.query.filter_by(faculty_id=faculty.id).delete()
    # Delete faculty
    db.session.delete(faculty)
    db.session.commit()
    flash(f"✅ Removed faculty account: {name}")
    return redirect(url_for("admin_faculty"))


@app.route("/admin/change_password", methods=["GET", "POST"])
@admin_required
def admin_change_password():
    if request.method == "POST":
        current  = request.form.get("current_password")
        new_pass = request.form.get("new_password")
        confirm  = request.form.get("confirm_password")
        admin    = Admin.query.filter_by(username=session["admin_username"]).first()

        if not check_password_hash(admin.password, current):
            flash("[ERROR] Current password is incorrect.")
        elif new_pass != confirm:
            flash("[ERROR] New passwords do not match.")
        else:
            admin.password = generate_password_hash(new_pass)
            db.session.commit()
            flash("[SUCCESS] Password changed successfully!")
    return render_template("admin_change_password.html")

if __name__ == "__main__":
    app.run(debug=False)