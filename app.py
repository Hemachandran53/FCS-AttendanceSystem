# app.py
import os
import json
import random
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='teacher')
    schedules = db.relationship('Schedule', backref='teacher', lazy=True)
    attendances = db.relationship('Attendance', backref='teacher', lazy=True)
    substitutions_assigned = db.relationship('Substitution', backref='substitute', 
                                           foreign_keys='Substitution.substitute_teacher_id', lazy=True)
    substitutions_needed = db.relationship('Substitution', backref='original_teacher', 
                                         foreign_keys='Substitution.original_teacher_id', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    class_name = db.Column(db.String(100), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Substitution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    substitute_teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    schedule = db.relationship('Schedule')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    weekday = today.strftime('%A')
    
    # Get today's schedule
    schedule = Schedule.query.filter_by(teacher_id=current_user.id, day=weekday).order_by(Schedule.period).all()
    
    # Check if teacher has marked attendance for today
    attendance = Attendance.query.filter_by(teacher_id=current_user.id, date=today).first()
    
    # Get substitution assignments for today
    substitutions = Substitution.query.filter_by(substitute_teacher_id=current_user.id, date=today).all()
    
    return render_template('dashboard.html', 
                          schedule=schedule, 
                          attendance=attendance, 
                          substitutions=substitutions,
                          today=today)

@app.route('/mark_attendance', methods=['POST'])
@login_required
def mark_attendance():
    status = request.form.get('status')
    today = date.today()
    
    # Check if attendance already marked
    existing = Attendance.query.filter_by(teacher_id=current_user.id, date=today).first()
    if existing:
        existing.status = status
    else:
        attendance = Attendance(teacher_id=current_user.id, date=today, status=status)
        db.session.add(attendance)
    
    db.session.commit()
    
    # If teacher is absent, assign substitutes
    if status == 'absent':
        assign_substitutes(current_user.id, today)
    
    flash('Attendance marked successfully')
    return redirect(url_for('dashboard'))

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    teachers = User.query.filter_by(role='teacher').all()
    today = date.today()
    
    # Get attendance for all teachers today
    attendance_dict = {}
    for teacher in teachers:
        att = Attendance.query.filter_by(teacher_id=teacher.id, date=today).first()
        attendance_dict[teacher.id] = att.status if att else 'Present'
    
    substitutions = Substitution.query.filter_by(date=today).all()
    
    return render_template('admin.html', 
                          teachers=teachers, 
                          attendance_dict=attendance_dict,
                          substitutions=substitutions,
                          today=today)

@app.route('/admin/teachers')
@login_required
def manage_teachers():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    teachers = User.query.all()
    return render_template('manage_teachers.html', teachers=teachers)

@app.route('/admin/teachers/add', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')
        role = request.form.get('role', 'teacher')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('add_teacher'))
        
        user = User(username=username, name=name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Teacher added successfully')
        return redirect(url_for('manage_teachers'))
    
    return render_template('add_teacher.html')

@app.route('/admin/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    teacher = User.query.get_or_404(id)
    
    if request.method == 'POST':
        teacher.username = request.form.get('username')
        teacher.name = request.form.get('name')
        teacher.role = request.form.get('role')
        
        new_password = request.form.get('password')
        if new_password:
            teacher.set_password(new_password)
        
        db.session.commit()
        flash('Teacher updated successfully')
        return redirect(url_for('manage_teachers'))
    
    return render_template('edit_teacher.html', teacher=teacher)

@app.route('/admin/schedules')
@login_required
def manage_schedules():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    schedules = db.session.query(Schedule).join(User).order_by(User.name, Schedule.day, Schedule.period).all()
    return render_template('manage_schedules.html', schedules=schedules)

@app.route('/admin/schedules/add', methods=['GET', 'POST'])
@login_required
def add_schedule():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        day = request.form.get('day')
        period = request.form.get('period')
        class_name = request.form.get('class_name')
        
        schedule = Schedule(teacher_id=teacher_id, day=day, period=int(period), class_name=class_name)
        db.session.add(schedule)
        db.session.commit()
        
        flash('Schedule added successfully')
        return redirect(url_for('manage_schedules'))
    
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('add_schedule.html', teachers=teachers)

@app.route('/admin/schedules/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_schedule(id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    schedule = Schedule.query.get_or_404(id)
    
    if request.method == 'POST':
        schedule.teacher_id = request.form.get('teacher_id')
        schedule.day = request.form.get('day')
        schedule.period = int(request.form.get('period'))
        schedule.class_name = request.form.get('class_name')
        
        db.session.commit()
        flash('Schedule updated successfully')
        return redirect(url_for('manage_schedules'))
    
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('edit_schedule.html', schedule=schedule, teachers=teachers)

@app.route('/admin/reports')
@login_required
def reports():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    # Get date range
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = date.today() - timedelta(days=7)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = date.today()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    attendances = db.session.query(Attendance, User).join(User).filter(
        Attendance.date >= start_date, 
        Attendance.date <= end_date
    ).order_by(Attendance.date.desc()).all()
    
    substitutions = Substitution.query.filter(
        Substitution.date >= start_date, 
        Substitution.date <= end_date
    ).all()
    
    return render_template('reports.html', 
                          attendances=attendances, 
                          substitutions=substitutions,
                          start_date=start_date,
                          end_date=end_date)

# Add these routes to your app.py file after the existing routes

@app.route('/admin/substitutions')
@login_required
def manage_substitutions():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    today = date.today()
    substitutions = db.session.query(Substitution).join(Schedule).order_by(Substitution.date.desc()).limit(50).all()
    return render_template('manage_substitutions.html', substitutions=substitutions, today=today)

@app.route('/admin/substitutions/add', methods=['GET', 'POST'])
@login_required
def add_substitution():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        schedule_id = request.form.get('schedule_id')
        substitute_teacher_id = request.form.get('substitute_teacher_id')
        sub_date = request.form.get('date')
        
        # Get the schedule to find the original teacher
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            flash('Invalid schedule selected')
            return redirect(url_for('add_substitution'))
        
        # Check if substitution already exists
        existing = Substitution.query.filter_by(
            schedule_id=schedule_id,
            date=datetime.strptime(sub_date, '%Y-%m-%d').date()
        ).first()
        
        if existing:
            flash('Substitution already exists for this class on this date')
            return redirect(url_for('add_substitution'))
        
        # Create substitution
        substitution = Substitution(
            original_teacher_id=schedule.teacher_id,
            substitute_teacher_id=substitute_teacher_id,
            schedule_id=schedule_id,
            date=datetime.strptime(sub_date, '%Y-%m-%d').date()
        )
        db.session.add(substitution)
        db.session.commit()
        
        flash('Substitution added successfully')
        return redirect(url_for('manage_substitutions'))
    
    # Get all teachers and schedules for the form
    teachers = User.query.filter_by(role='teacher').all()
    schedules = db.session.query(Schedule).join(User).order_by(User.name, Schedule.day, Schedule.period).all()
    return render_template('add_substitution.html', teachers=teachers, schedules=schedules)

@app.route('/admin/substitutions/delete/<int:id>')
@login_required
def delete_substitution(id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    substitution = Substitution.query.get_or_404(id)
    db.session.delete(substitution)
    db.session.commit()
    
    flash('Substitution deleted successfully')
    return redirect(url_for('manage_substitutions'))

# Also add this route to mark a teacher absent and trigger automatic substitution
@app.route('/admin/mark_absent', methods=['POST'])
@login_required
def admin_mark_absent():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    teacher_id = request.form.get('teacher_id')
    absent_date = request.form.get('date')
    
    if not absent_date:
        absent_date = date.today()
    else:
        absent_date = datetime.strptime(absent_date, '%Y-%m-%d').date()
    
    # Check if attendance already marked
    existing = Attendance.query.filter_by(teacher_id=teacher_id, date=absent_date).first()
    if existing:
        existing.status = 'absent'
    else:
        attendance = Attendance(teacher_id=teacher_id, date=absent_date, status='absent')
        db.session.add(attendance)
    
    db.session.commit()
    
    # Assign substitutes
    assign_substitutes(int(teacher_id), absent_date)
    
    flash('Teacher marked absent and substitutes assigned')
    return redirect(url_for('admin_panel'))                          

# Substitution logic
def assign_substitutes(teacher_id, date_obj):
    weekday = date_obj.strftime('%A')
    
    # Find all periods for the absent teacher on this day
    schedules = Schedule.query.filter_by(teacher_id=teacher_id, day=weekday).all()
    
    for schedule in schedules:
        # Find teachers who are present today
        present_teachers = db.session.query(User).filter(
            User.role == 'teacher',
            User.id != teacher_id
        ).all()
        
        # Filter out teachers who are absent
        available_teachers = []
        for teacher in present_teachers:
            att = Attendance.query.filter_by(teacher_id=teacher.id, date=date_obj).first()
            if not att or att.status != 'absent':
                # Check if teacher is free during this period
                conflict = Schedule.query.filter_by(
                    teacher_id=teacher.id, 
                    day=weekday, 
                    period=schedule.period
                ).first()
                if not conflict:
                    available_teachers.append(teacher)
        
        # Assign substitute if available
        if available_teachers:
            substitute = random.choice(available_teachers)
            substitution = Substitution(
                original_teacher_id=teacher_id,
                substitute_teacher_id=substitute.id,
                schedule_id=schedule.id,
                date=date_obj
            )
            db.session.add(substitution)
    
    db.session.commit()

# Initialize database with sample data
# In app.py, update the init_db() function to add some weekend schedules
def init_db():
    db.create_all()
    
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', name='Admin User', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Add sample teachers
        teachers = [
            {'username': 'teacher1', 'name': 'John Smith', 'password': 'pass123'},
            {'username': 'teacher2', 'name': 'Jane Doe', 'password': 'pass123'},
            {'username': 'teacher3', 'name': 'Bob Johnson', 'password': 'pass123'},
            {'username': 'Samantha', 'name': 'Samantha Prabhu', 'password': 'pass123'},
        ]
        
        for t in teachers:
            teacher = User(username=t['username'], name=t['name'], role='teacher')
            teacher.set_password(t['password'])
            db.session.add(teacher)
        
        db.session.commit()
        
        # Add sample schedules including weekends
        teacher1 = User.query.filter_by(username='teacher1').first()
        teacher2 = User.query.filter_by(username='teacher2').first()
        teacher3 = User.query.filter_by(username='teacher3').first()
        teacher4 = User.query.filter_by(username='Samantha').first()
        
        schedules = [
            # Teacher 1 (John Smith) schedules
            {'teacher_id': teacher1.id, 'day': 'Monday', 'period': 1, 'class_name': 'Math 101'},
            {'teacher_id': teacher1.id, 'day': 'Monday', 'period': 2, 'class_name': 'Math 202'},
            {'teacher_id': teacher1.id, 'day': 'Tuesday', 'period': 3, 'class_name': 'Math 101'},
            {'teacher_id': teacher1.id, 'day': 'Wednesday', 'period': 1, 'class_name': 'Math 303'},
            {'teacher_id': teacher1.id, 'day': 'Friday', 'period': 1, 'class_name': 'English'},
            {'teacher_id': teacher1.id, 'day': 'Saturday', 'period': 1, 'class_name': 'Math Special Class'},
            
            # Teacher 2 (Jane Doe) schedules
            {'teacher_id': teacher2.id, 'day': 'Monday', 'period': 3, 'class_name': 'Science 101'},
            {'teacher_id': teacher2.id, 'day': 'Tuesday', 'period': 1, 'class_name': 'Science 202'},
            {'teacher_id': teacher2.id, 'day': 'Wednesday', 'period': 2, 'class_name': 'Science 101'},
            {'teacher_id': teacher2.id, 'day': 'Saturday', 'period': 2, 'class_name': 'Science Lab'},
            
            # Teacher 3 (Bob Johnson) schedules
            {'teacher_id': teacher3.id, 'day': 'Monday', 'period': 4, 'class_name': 'History 101'},
            {'teacher_id': teacher3.id, 'day': 'Tuesday', 'period': 2, 'class_name': 'History 202'},
            {'teacher_id': teacher3.id, 'day': 'Wednesday', 'period': 3, 'class_name': 'History 101'},
            {'teacher_id': teacher3.id, 'day': 'Sunday', 'period': 1, 'class_name': 'History Workshop'},
            
            # Teacher 4 (Samantha) schedules
            {'teacher_id': teacher4.id, 'day': 'Friday', 'period': 2, 'class_name': 'Maths'},
            {'teacher_id': teacher4.id, 'day': 'Sunday', 'period': 2, 'class_name': 'Maths Tutorial'},
        ]
        
        for s in schedules:
            schedule = Schedule(**s)
            db.session.add(schedule)
        
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)