from flask import Flask, jsonify
from config import Config
from models import db, Admin
from flask_login import LoginManager
from flask_cors import CORS

from routes import (
    signup, login, logout,
    forgot_password, reset_password,
    create_opportunity, get_opportunities,
    get_opportunity, update_opportunity, delete_opportunity
)

app = Flask(__name__)
app.config.from_object(Config)

app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

CORS(app, supports_credentials=True)

db.init_app(app)

# Routes
app.add_url_rule('/signup', 'signup', signup, methods=['POST'])
app.add_url_rule('/login', 'login', login, methods=['POST'])
app.add_url_rule('/logout', 'logout', logout, methods=['POST'])
app.add_url_rule('/forgot-password', 'forgot_password', forgot_password, methods=['POST'])
app.add_url_rule('/reset-password/<token>', 'reset_password', reset_password, methods=['POST'])

app.add_url_rule('/opportunities', 'create_opportunity', create_opportunity, methods=['POST'])
app.add_url_rule('/opportunities', 'get_opportunities', get_opportunities, methods=['GET'])
app.add_url_rule('/opportunities/<int:op_id>', 'get_opportunity', get_opportunity, methods=['GET'])
app.add_url_rule('/opportunities/<int:op_id>', 'update_opportunity', update_opportunity, methods=['PUT'])
app.add_url_rule('/opportunities/<int:op_id>', 'delete_opportunity', delete_opportunity, methods=['DELETE'])

@app.route('/')
def home():
    return "Backend is running "


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized"}), 401

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

with app.app_context():
    db.create_all()
