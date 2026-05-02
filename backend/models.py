from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    opportunities = db.relationship('Opportunity', backref='creator', lazy=True)

    def __repr__(self):
        return f"<Admin {self.email}>"


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.String(50), nullable=False)

    start_date = db.Column(db.Date, nullable=False)

    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)

    category = db.Column(db.Enum(
        "Technology",
        "Business",
        "Design",
        "Marketing",
        "Data Science",
        "Other",
        name="category_enum"
    ), nullable=False)

    future_opportunities = db.Column(db.Text, nullable=False)
    max_applicants = db.Column(db.Integer, nullable=True)

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)

    def __repr__(self):
        return f"<Opportunity {self.name}>"