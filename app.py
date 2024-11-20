from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from waitress import serve
from dotenv import load_dotenv
import os
import bcrypt

# Load environment variables from .env
load_dotenv()

# Define your Flask app object
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SERVER_NAME'] = 'server-admin-project.sbs'

# Configure Database for MySQL on Railway
# Use the DATABASE_URL environment variable for Railway MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:RsKQJaLaEsaXAoWwLqFYWcbdpwWfsnaC@autorack.proxy.rlwy.net:22642/railway"
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Use DATABASE_URL from .env
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set session cookie domain for both main domain and subdomain
app.config['SESSION_COOKIE_DOMAIN'] = '.server-admin-project.sbs'

# Initialize the database
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Routes
@app.route('/', subdomain="sub")
def subdomain_home():
    return "Welcome to the Subdomain!"

@app.route('/')
def main_home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Server-side validation
        if len(username) < 3 or len(username) > 20:
            return "Username must be between 3 and 20 characters!"
        
        if len(password) < 8:
            return "Password must be at least 8 characters long!"

        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            return "User already exists!"
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store the user with the hashed password
        new_user = User(username=username, password=hashed_password.decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main_home'))
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Fetch the user from the database
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    return "Invalid credentials!"

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')

# This is where we call `serve()` from Waitress to run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    serve(app, host='0.0.0.0', port=8080)
