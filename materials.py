import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study_materials")

SUBJECTS = {
    "CSE": {
         "1st Year": {
            "Semester 1": [
                {"code": "HS3152", "name": "Professional English - I"},
                {"code": "MA3151", "name": "Matrices and Calculus"},
                {"code": "PH3151", "name": "Engineering Physics"},
                {"code": "CY3151", "name": "Engineering Chemistry"},
                {"code": "GE3151", "name": "Problem Solving and Python Programming"},
                {"code": "GE3152", "name": "Heritage of Tamils"},
            ],
            "Semester 2": [
                {"code": "HS3252", "name": "Professional english - II"},
                {"code": "MA3251", "name": "Statistics and numerical methods"},
                {"code": "PH3256", "name": "Physics for Information Science"},
                {"code": "BE3251", "name": "Basic Electrical and Electronics Engineering"},
                {"code": "GE3251", "name": "Engineering graphics"},
                {"code": "CS3251", "name": "Programming in C"},
                {"code": "GE3252", "name": "Tamils and Technology"},
            ],
         },
        "2nd Year": {
            "Semester 3": [
                {"code": "MA3354", "name": "Discrete Mathematics"},
                {"code": "CS3301", "name": "Data Structures"},
                {"code": "CS3391", "name": "Object Oriented Programming"},
                {"code": "CS3351", "name": "Digital Principles and Computer Organization"},
                {"code": "CS3352", "name": "Foundations of Data Science"},
            ],
            "Semester 4": [
                {"code": "CS3452", "name": "Theory of Computation"},
                {"code": "CS3491", "name": "Artificial Intelligence and Machine Learning"},
                {"code": "CS3492", "name": "Database Management Systems"},
                {"code": "CS3401", "name": "Algorithms"},
                {"code": "CS3451", "name": "Introduction to Operating Systems"},
                {"code": "GE3451", "name": "Environmental Sciences and Sustainability"},
             
            ],
        },
        "3rd Year": {
            "Semester 5": [
                {"code": "CS3501", "name": "Compiler Design"},
                {"code": "CS3591", "name": "Computer Networks"},
                {"code": "CB3491", "name": "Cryptography and Cyber Security"},
                {"code": "CS3551", "name": "Distributed Computing"},
            ],
            "Semester 6": [
                {"code": "CCS356", "name": "Object Oriented Software Engineering"},
                {"code": "CS3691", "name": "Embedded Systems and IoT"},
            ],
        },
        "4th Year": {
            "Semester 7": [
                {"code": "GE3791", "name": "Human Values and Ethics"},
                {"code": "OBT356", "name": "Lifestyle Disease"},
                {"code": "AI3021", "name": "IT in Agricultural System"},
                {"code": "GE3752", "name": "Total Quality Management"},
                {"code": "GE3751", "name": "Principles of Management"},
            ],
            "Semester 8": [],
        },
    },
    "IT": {
        "1st Year": {
            "Semester 1": [
                {"code": "HS3152", "name": "Professional English - I"},
                {"code": "MA3151", "name": "Matrices and Calculus"},
                {"code": "PH3151", "name": "Engineering Physics"},
                {"code": "CY3151", "name": "Engineering Chemistry"},
                {"code": "GE3151", "name": "Problem Solving and Python Programming"},
                {"code": "GE3152", "name": "Heritage of Tamils"},
            ],
            "Semester 2": [
                {"code": "HS3252", "name": "Professional english - II"},
                {"code": "MA3251", "name": "Statistics and numerical methods"},
                {"code": "PH3256", "name": "Physics for Information Science"},
                {"code": "BE3251", "name": "Basic Electrical and Electronics Engineering"},
                {"code": "GE3251", "name": "Engineering graphics"},
                {"code": "CS3251", "name": "Programming in C"},
                {"code": "GE3252", "name": "Tamils and Technology"},
            ],
        },
        "2nd Year": {
            "Semester 3": [
                {"code": "CD3291", "name": "Data Structures and Algorithms"},
                {"code": "MA3354", "name": "Discrete Mathematics"},
                {"code": "CS3391", "name": "Object Oriented Programming"},
                {"code": "CS3351", "name": "Digital Principles and Computer Organization"},
                {"code": "CS3352", "name": "Foundations of Data Science"},
            ],
            "Semester 4": [
                {"code": "IT3401", "name": "Web Essentials"},
                {"code": "CS3452", "name": "Theory of Computation"},
                {"code": "CS3491", "name": "Artificial Intelligence and Machine Learning"},
                {"code": "CS3492", "name": "Database Management Systems"},
                {"code": "CS3451", "name": "Introduction to Operating Systems"},
                {"code": "GE3451", "name": "Environmental Sciences and Sustainability"},
            ],
        },
        "3rd Year": {
            "Semester 5": [
                {"code": "IT3501", "name": " Full Stack Web Development "},
                {"code": "CS3501", "name": "Compiler Design"},
                {"code": "CS3591", "name": "Computer Networks"},
                {"code": "CB3491", "name": "Cryptography and Cyber Security"},
                {"code": "CS3551", "name": "Distributed Computing"},
            ],
            "Semester 6": [
                {"code": "CCS356", "name": "Object Oriented Software Engineering"},
                {"code": "CS3691", "name": "Embedded Systems and IoT"},
            ],
        },
        "4th Year": {
            "Semester 7": [
                {"code": "GE3791", "name": "Human Values and Ethics"},
                {"code": "OBT356", "name": "Lifestyle Disease"},
                {"code": "AI3021", "name": "IT in Agricultural System"},
                {"code": "GE3752", "name": "Total Quality Management"},
                {"code": "GE3751", "name": "Principles of Management"},
            ],
            "Semester 8": [],
        },
    }
}



def get_subjects(department, year, semester):
    try:
        from app import app, Subject
        with app.app_context():
            subjects = Subject.query.filter_by(
                department=department,
                year=year,
                semester=semester
            ).order_by(Subject.subject_code).all()
            return [{"code": s.subject_code, "name": s.subject_name} for s in subjects]
    except Exception as e:
        print("Error fetching subjects:", e)
        return []


def list_material_files(department, course_level, regulation, year, semester, subject_code, file_type):
    """
    Returns a sorted list of all uploaded PDFs for a given file_type.
    New path: study_materials/[Dept]/[CourseLevel]/[Regulation]/[Year]/...
    """
    folder = os.path.join(BASE, department, course_level, regulation, year, semester, subject_code)
    files = []
    
    # Legacy Migration Check
    if not os.path.exists(folder):
        # Check level 1 legacy: [Dept]/[Reg]/[Year]/... (old regulation standard)
        legacy_reg_folder = os.path.join(BASE, department, regulation, year, semester, subject_code)
        if os.path.exists(legacy_reg_folder):
            folder = legacy_reg_folder
        else:
            # Check level 2 legacy: [Dept]/[Year]/... (pre-regulation standard)
            legacy_folder = os.path.join(BASE, department, year, semester, subject_code)
            if os.path.exists(legacy_folder):
                folder = legacy_folder
            
    if not os.path.exists(folder):
        return files

    # Scan all files in folder and pick indexed ones matching {file_type}_N.pdf
    prefix = f"{file_type}_"
    for fname in sorted(os.listdir(folder)):
        if fname.startswith(prefix) and fname.endswith(".pdf"):
            try:
                idx = int(fname[len(prefix):-4])  # extract N from notes_N.pdf
                files.append({"index": idx, "path": os.path.join(folder, fname)})
            except ValueError:
                continue
    files.sort(key=lambda x: x["index"])

    # Fallback: legacy single file (notes.pdf) when no indexed files exist
    if not files:
        legacy = os.path.join(folder, f"{file_type}.pdf")
        if os.path.exists(legacy):
            files.append({"index": 1, "path": legacy})
    return files


def get_next_index(department, course_level, regulation, year, semester, subject_code, file_type):
    """
    Returns the next available index for a file_type upload.
    Also migrates a legacy single file to _1 naming on first new upload.
    """
    folder = os.path.join(BASE, department, course_level, regulation, year, semester, subject_code)
    os.makedirs(folder, exist_ok=True)

    # Migrate legacy file (notes.pdf -> notes_1.pdf) if it exists and no indexed files yet
    legacy = os.path.join(folder, f"{file_type}.pdf")
    indexed_1 = os.path.join(folder, f"{file_type}_1.pdf")
    if os.path.exists(legacy) and not os.path.exists(indexed_1):
        os.rename(legacy, indexed_1)

    # Find next free index
    idx = 1
    while os.path.exists(os.path.join(folder, f"{file_type}_{idx}.pdf")):
        idx += 1
    return idx


def get_material_path(department, course_level, regulation, year, semester, subject_code, file_type):
    """
    Returns path of the FIRST available file for a type (legacy compatibility).
    Supports both indexed (notes_1.pdf) and legacy (notes.pdf) files.
    """
    files = list_material_files(department, course_level, regulation, year, semester, subject_code, file_type)
    if files:
        return files[0]["path"]
    return None


def get_available_materials(department, course_level, regulation, year, semester, subject_code):
    """
    Returns count of uploaded files per material type, along with URLs for all files to build view links.
    """
    from urllib.parse import quote
    types = ["notes", "pyq", "syllabus", "question_bank"]
    result = {}
    for t in types:
        files = list_material_files(department, course_level, regulation, year, semester, subject_code, t)
        
        view_prefix = "view_question_bank" if t == "question_bank" else f"view_{t}"
        urls = []
        for f in files:
            idx = f["index"]
            url = f"/{view_prefix}/{quote(department)}/{quote(course_level)}/{quote(regulation)}/{quote(year)}/{quote(semester)}/{quote(subject_code)}/{idx}"
            urls.append({"index": idx, "url": url})
            
        result[t] = {
            "count": len(files),
            "urls": urls
        }
    return result


def list_all_subjects():
    """
    Returns a flat list of all subjects across all
    departments, years and semesters — useful for admin panel.
    """
    all_subjects = []
    try:
        from app import app, Subject
        with app.app_context():
            subjects = Subject.query.order_by(Subject.department, Subject.year, Subject.semester, Subject.subject_code).all()
            for s in subjects:
                all_subjects.append({
                    "id":         s.id,
                    "department": s.department,
                    "year":       s.year,
                    "semester":   s.semester,
                    "code":       s.subject_code,
                    "name":       s.subject_name,
                    "course_level": s.course_level,
                    "materials":  get_available_materials(
                                      s.department, s.course_level, "R2021", s.year, s.semester, s.subject_code
                                  )
                })
    except Exception as e:
        print("Error in list_all_subjects:", e)
    return all_subjects