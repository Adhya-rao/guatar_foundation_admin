from flask import request, jsonify, current_app
from models import db, Admin, Opportunity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
import re
from flask import session

def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False)

    user = Admin.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user, remember=remember)

    session['user_id'] = user.id
    session.permanent = True
    session.modified = True

    return jsonify({"message": "Login successful"}), 200

def signup():
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    if not all([full_name, email, password, confirm_password]):
        return jsonify({"error": "All fields are required"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email"}), 400
    if Admin.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400
    hashed_password = generate_password_hash(password)
    new_admin = Admin(full_name=full_name, email=email, password_hash=hashed_password)
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({"message": "Signup successful"}), 201

@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

def forgot_password():
    data = request.get_json()
    email = data.get('email')
    message = {"message": "If this email exists, a reset link has been generated"}
    if not email:
        return jsonify(message), 200
    user = Admin.query.filter_by(email=email).first()
    if user:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])
        reset_link = f"http://127.0.0.1:5000/reset-password/{token}"
        print("\n RESET LINK (valid 1 hour):")
        print(reset_link)
        print()
        return jsonify({"message": message["message"], "reset_link": reset_link}), 200
    return jsonify(message), 200

def reset_password(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
    except Exception:
        return jsonify({"error": "Reset link expired or invalid"}), 400
    data = request.get_json()
    new_password = data.get('password')
    confirm_password = data.get('confirm_password')
    if not new_password or len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    user = Admin.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"message": "Password reset successful"}), 200
@login_required
def create_opportunity():
    data = request.get_json()

    name = data.get('name')
    duration = data.get('duration')
    start_date = data.get('start_date')
    description = data.get('description')
    skills = data.get('skills')
    category = data.get('category')
    future_opportunities = data.get('future_opportunities')
    max_applicants = data.get('max_applicants')

    if not all([name, duration, start_date, description, skills, category, future_opportunities]):
        return jsonify({"error": "All required fields must be filled"}), 400

    category = category.strip().lower()

    mapping = {
        "data": "data science",
        "datascience": "data science"
    }

    category = mapping.get(category, category)

    valid_categories = ["technology", "business", "design", "marketing", "data science", "other"]

    if category not in valid_categories:
        return jsonify({"error": f"Invalid category: {category}"}), 400

    category = category.title()

    from datetime import datetime
    start_date = datetime.strptime(start_date, "%Y-%m-%d")

    if max_applicants:
        max_applicants = int(max_applicants)

    try:
        new_op = Opportunity(
            name=name,
            duration=duration,
            start_date=start_date,
            description=description,
            skills=skills,
            category=category,
            future_opportunities=future_opportunities,
            max_applicants=max_applicants,
            admin_id=current_user.id
        )

        db.session.add(new_op)
        db.session.commit()

        return jsonify({"message": "Opportunity created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@login_required
def get_opportunities():
     print("DEBUG:", current_user.is_authenticated, current_user.id)

    ops = Opportunity.query.filter_by(admin_id=current_user.id).all()
  
    result = []
    for op in ops:
        result.append({
            "id": op.id,
            "name": op.name,
            "category": op.category,
            "duration": op.duration,
            "start_date": op.start_date,
            "description": op.description,
            "skills": op.skills,
            "future_opportunities": op.future_opportunities,
            "max_applicants": op.max_applicants
        })
    return jsonify(result), 200

@login_required
def get_opportunity(op_id):
    
    op = Opportunity.query.filter_by(id=op_id, admin_id=current_user.id).first()
    if not op:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "id": op.id,
        "name": op.name,
        "duration": op.duration,
        "start_date": op.start_date,
        "description": op.description,
        "skills": op.skills,
        "category": op.category,
        "future_opportunities": op.future_opportunities,
        "max_applicants": op.max_applicants
    }), 200
@login_required
def update_opportunity(op_id):
    op = Opportunity.query.filter_by(id=op_id, admin_id=current_user.id).first()
    if not op:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    valid_categories = ["technology", "business", "design", "marketing", "data science", "other"]

    category = data.get('category')
    if category:
        category = category.strip().lower()

        mapping = {
            "data": "data science",
            "datascience": "data science"
        }

        category = mapping.get(category, category)

        if category not in valid_categories:
            return jsonify({"error": "Invalid category"}), 400

        op.category = category.title()

    op.name = data.get('name', op.name)
    op.duration = data.get('duration', op.duration)
    op.start_date = data.get('start_date', op.start_date)
    op.description = data.get('description', op.description)
    op.skills = data.get('skills', op.skills)
    op.future_opportunities = data.get('future_opportunities', op.future_opportunities)

    max_applicants = data.get('max_applicants')
    if max_applicants:
        op.max_applicants = int(max_applicants)

    db.session.commit()
    return jsonify({"message": "Updated successfully"}), 200
   

@login_required
def delete_opportunity(op_id):
    op = Opportunity.query.filter_by(id=op_id, admin_id=current_user.id).first()
    if not op:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(op)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"}), 200
