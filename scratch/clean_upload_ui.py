import re

with open(r'd:\proj\templates\admin_upload.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the previously injected blocks
# The injected block starts with:
#       {% if session.get('faculty_logged_in') and assigned_subject %}
# and ends with:
#       {% endif %}
# surrounding a single <div class="grid2">.
# Wait, let's just replace the injected string with \1.

bad_injection = re.compile(
r'\s*\{% if session\.get\(\'faculty_logged_in\'\) and assigned_subject %\}'
r'.*?Uploading for: \{\{ assigned_subject\.subject_code \}\}.*?'
r'\{% else %\}(.*?)'
r'\s*\{% endif %\}', re.DOTALL)

cleaned_content = bad_injection.sub(r'\1', content)

with open(r'd:\proj\templates\admin_upload.html', 'w', encoding='utf-8') as f:
    f.write(cleaned_content)
print("Cleaned!")
