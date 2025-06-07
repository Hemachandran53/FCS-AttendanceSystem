# setup.py
import os
import sys

def create_project_structure():
    """Create the project directory structure"""
    directories = [
        'static',
        'static/js',
        'templates'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    print("Setting up Attendance Management System...")
    
    # Create directory structure
    create_project_structure()
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("\nCreating virtual environment...")
        os.system(f"{sys.executable} -m venv venv")
    
    # Determine the pip path based on OS
    if sys.platform == "win32":
        pip_path = os.path.join('venv', 'Scripts', 'pip')
        python_path = os.path.join('venv', 'Scripts', 'python')
    else:
        pip_path = os.path.join('venv', 'bin', 'pip')
        python_path = os.path.join('venv', 'bin', 'python')
    
    # Install requirements
    print("\nInstalling requirements...")
    os.system(f"{pip_path} install -r requirements.txt")
    
    print("\n✅ Setup complete!")
    print("\nTo run the application:")
    print(f"1. Activate virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print(f"2. Run the application:")
    print("   python app.py")
    print("\n3. Open browser and go to: http://127.0.0.1:5000")
    print("\nDefault credentials:")
    print("   Admin: admin/admin123")
    print("   Teachers: teacher1/pass123, teacher2/pass123, etc.")

if __name__ == "__main__":
    main()