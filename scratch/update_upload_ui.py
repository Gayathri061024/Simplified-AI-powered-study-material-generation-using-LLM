import re

with open(r'd:\proj\templates\admin_upload.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """
      {% if session.get('faculty_logged_in') and assigned_subject %}
        <div class="alert success" style="margin-bottom: 24px; padding: 16px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px;">
          <strong style="color: #166534; font-size: 16px;">Uploading for: {{ assigned_subject.subject_code }} - {{ assigned_subject.subject_name }}</strong><br>
          <span style="color: #15803d; font-size: 13px;">{{ assigned_subject.department }} • {{ assigned_subject.year }} • {{ assigned_subject.semester }}</span>
        </div>
        <input type="hidden" name="course_level" class="level-select" value="{{ assigned_subject.course_level }}">
        <input type="hidden" name="regulation" class="reg-select" value="R2021">
        <input type="hidden" name="department" class="dept-select" value="{{ assigned_subject.department }}">
        <input type="hidden" name="year" class="year-select" value="{{ assigned_subject.year }}">
        <input type="hidden" name="semester" class="sem-select" value="{{ assigned_subject.semester }}">
        <input type="hidden" name="subject_code" class="sub-code" value="{{ assigned_subject.subject_code }}">
      {% else %}
\\1
      {% endif %}
      <div class="form-group">
"""

# We look for a block that starts with <div class="grid2"> and ends with </div> \s* </div> \s* <div class="form-group">
# BUT we want to capture ALL grid2 blocks inside a form.
# A better way is:
# match everything between `<form ...>` and `<div class="form-group"> \n <label>(Upload|PDF Asset Source)`
# No, let's match `<div class="grid2">` up to `</select>\s*</div>\s*</div>\s*<div class="form-group">`
# Actually, the last grid2 ends with `</div>` (for the sub-code form-group) and then `</div>` (for the grid2 itself).
# Then comes `<div class="form-group">` for the file input.

pattern = re.compile(r'(<div class="grid2">.*?</select>\s*</div>\s*</div>)\s*<div class="form-group">', re.DOTALL)

def replacer(match):
    original_grid_content = match.group(1)
    if "{% if session.get('faculty_logged_in') and assigned_subject %}" in original_grid_content:
        return match.group(0)
    return replacement.replace('\\1', original_grid_content)

new_content = pattern.sub(replacer, content)

with open(r'd:\proj\templates\admin_upload.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated admin_upload.html correctly.")
