from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_recruiter = db.Column(db.Boolean, default=False)
    resumes = db.relationship('Resume', backref='user', lazy=True)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(100), nullable=False)
    cover_letter = db.Column(db.Text)
    skills = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_recruiter = request.form.get('type') == 'recruiter'
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password) and user.is_recruiter == is_recruiter:
            session['user_id'] = user.id
            session['is_recruiter'] = user.is_recruiter
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials or wrong account type.')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_recruiter = request.form.get('type') == 'recruiter'
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('register'))
        
        user = User(
            email=email,
            password=generate_password_hash(password),
            is_recruiter=is_recruiter
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    if user.is_recruiter:
        resumes = Resume.query.all()
        return render_template('recruiter_dashboard.html', resumes=resumes)
    else:
        resumes = Resume.query.filter_by(user_id=user.id).all()
        return render_template('applicant_dashboard.html', resumes=resumes)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/submit_resume', methods=['POST'])
@login_required
def submit_resume():
    user = User.query.get(session['user_id'])
    if user.is_recruiter:
        return redirect(url_for('dashboard'))
    
    resume = Resume(
        user_id=user.id,
        name=request.form.get('name'),
        email=request.form.get('email'),
        job_title=request.form.get('jobTitle'),
        location=request.form.get('location'),
        industry=request.form.get('industry'),
        experience=request.form.get('experience'),
        cover_letter=request.form.get('coverLetter'),
        skills=request.form.get('skills')
    )
    db.session.add(resume)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/update_resume/<int:id>', methods=['GET', 'POST'])
@login_required
def update_resume(id):
    user = User.query.get(session['user_id'])
    resume = Resume.query.get_or_404(id)
    
    if resume.user_id != user.id:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        resume.name = request.form.get('name')
        resume.email = request.form.get('email')
        resume.job_title = request.form.get('job_title')
        resume.location = request.form.get('location')
        resume.industry = request.form.get('industry')
        resume.experience = request.form.get('experience')
        resume.cover_letter = request.form.get('cover_letter')
        resume.skills = request.form.get('skills')
        
        db.session.commit()
        flash('Resume updated successfully.')
        return redirect(url_for('dashboard'))
    
    return render_template('update.html', resume=resume)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)