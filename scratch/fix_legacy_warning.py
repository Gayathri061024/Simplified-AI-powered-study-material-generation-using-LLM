import re

def fix_deprecation():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace Model.query.get(id) with db.session.get(Model, id)
    # Using regex to capture the Model name and the id
    content = re.sub(r'([A-Z][A-Za-z0-9_]*)\.query\.get\(([^)]+)\)', 
                     r'db.session.get(\1, \2)', 
                     content)

    # Replace Model.query.get_or_404(id) with db.get_or_404(Model, id)
    content = re.sub(r'([A-Z][A-Za-z0-9_]*)\.query\.get_or_404\(([^)]+)\)', 
                     r'db.get_or_404(\1, \2)', 
                     content)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_deprecation()
    print("Fixed SQLAlchemy deprecation warnings.")
