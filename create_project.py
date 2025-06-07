# create_project.py - Run this to create the complete project
import os
import zipfile

def create_complete_project():
    """Create all project files with content"""
    
    # Create directories
    os.makedirs('attendance_app/static/js', exist_ok=True)
    os.makedirs('attendance_app/templates', exist_ok=True)
    
    # Write app.py (you'll need to copy the complete app.py content here)
    with open('attendance_app/app.py', 'w') as f:
        f.write('''# Copy the complete app.py content from above here''')
    
    # Write requirements.txt
    with open('attendance_app/requirements.txt', 'w') as f:
        f.write('''Flask==2.3.2
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
Werkzeug==2.3.6''')
    
    # Write all template files (copy content from above)
    templates = {
        'base.html': '''<!-- Copy base.html content -->''',
        'login.html': '''<!-- Copy login.html content -->''',
        'dashboard.html': '''<!-- Copy dashboard.html content -->''',
        'admin.html': '''<!-- Copy admin.html content -->''',
        'manage_teachers.html': '''<!-- Copy manage_teachers.html content -->''',
        'add_teacher.html': '''<!-- Copy add_teacher.html content -->''',
        'edit_teacher.html': '''<!-- Copy edit_teacher.html content -->''',
        'manage_schedules.html': '''<!-- Copy manage_schedules.html content -->''',
        'add_schedule.html': '''<!-- Copy add_schedule.html content -->''',
        'edit_schedule.html': '''<!-- Copy edit_schedule.html content -->''',
        'manage_substitutions.html': '''<!-- Copy manage_substitutions.html content -->''',
        'add_substitution.html': '''<!-- Copy add_substitution.html content -->''',
        'reports.html': '''<!-- Copy reports.html content -->'''
    }
    
    for filename, content in templates.items():
        with open(f'attendance_app/templates/{filename}', 'w') as f:
            f.write(content)
    
    # Write main.js
    with open('attendance_app/static/js/main.js', 'w') as f:
        f.write('''// Copy main.js content from above''')
    
    # Create zip file
    with zipfile.ZipFile('attendance_app.zip', 'w') as zipf:
        for root, dirs, files in os.walk('attendance_app'):
            for file in files:
                zipf.write(os.path.join(root, file))
    
    print("Project created successfully! Check attendance_app.zip")

if __name__ == "__main__":
    create_complete_project()