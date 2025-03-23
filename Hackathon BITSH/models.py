from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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

def setup_database(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
