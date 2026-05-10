import os
from materials import list_material_files

def test():
    dept = "CSE"
    level = "UG"
    reg = "R2021"
    year = "1st Year"
    sem = "Semester 1"
    code = "GE3151"
    
    print(f"Testing GE3151 retrieval...")
    files = list_material_files(dept, level, reg, year, sem, code, "notes")
    print(f"Found {len(files)} files for GE3151 Notes.")
    if files:
        for f in files:
            print(f" - {f['path']}")
    else:
        # Check if the path exists manually
        manual_path = os.path.join("study_materials", dept, year, sem, code)
        print(f"Manual path exist check ({manual_path}): {os.path.exists(manual_path)}")
        if os.path.exists(manual_path):
             print(f"Contents of {manual_path}: {os.listdir(manual_path)}")

if __name__ == "__main__":
    test()
