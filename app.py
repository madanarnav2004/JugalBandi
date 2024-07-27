import datetime
import string
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import pytz
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=True)
    fullname = db.Column(db.String(120), nullable=True)
    gender = db.Column(db.String(20), nullable=True) 
    age = db.Column(db.Integer, nullable=True)
    college = db.Column(db.String(120), nullable=True)
    field_of_study = db.Column(db.String(120), nullable=True)
    move_in_date = db.Column(db.Date, nullable=True) 
    bio = db.Column(db.Text, nullable=True)
    interests = db.Column(db.String(255), nullable=True)
    interested_in = db.Column(db.String(50), nullable=True) 
    profile_photo_url = db.Column(db.String(255), nullable=True)


    def __repr__(self):
        return '<User %r>' % self.username

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Kolkata')))
    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    image_count = 15  # Number of images
    image_files = [f'image{i}.jpg' for i in range(1, image_count + 1)]
    return render_template('index.html', image_files=image_files)

@app.route('/loading')
def loading():
    image_count = 15  # Number of images
    image_files = [f'image{i}.jpg' for i in range(1, image_count + 1)]
    return render_template('loading.html', image_files=image_files)

@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_submit():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if not username or not email or not password:
        flash("Please fill out all fields.", 'error')
        return redirect(url_for('signup'))

    hashed_password = generate_password_hash(password)

    try:
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Sign up successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    except IntegrityError as e:
        db.session.rollback()
        flash('Email already exists. Please use a different email.', 'error')
        return redirect(url_for('signup'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please enter your email and password.', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('login'))

        # Login successful, store user ID in session
        session['user_id'] = user.id
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for('profile'))  # Redirect to profile page

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Clear session and log out user
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route to display the board of profiles
@app.route('/board', methods=['GET'])
@login_required
def board():
    # Get query parameters for filtering
    college = request.args.get('college')
    gender = request.args.get('gender')

    # Query users based on filters
    users_query = User.query
    if college:
        users_query = users_query.filter_by(college=college)
    if gender:
        users_query = users_query.filter_by(gender=gender)
    
    users = users_query.all()
    
    return render_template('board.html', users=users, college=college, gender=gender)
# In app.py

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    recipient_id = request.json.get('recipient_id')
    message_text = request.json.get('message')

    if not recipient_id or not message_text:
        return jsonify({'error': 'Missing recipient or message'}), 400

    try:
        new_message = Message(
            sender_id=session['user_id'],
            recipient_id=recipient_id,
            message=message_text
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/get_matches')
@login_required
def get_matches():
    current_user = User.query.get(session['user_id'])
    college_filter = request.args.get('college', '')
    gender_filter = request.args.get('gender', '')

    query = User.query.filter(User.id != current_user.id)
    if college_filter:
        query = query.filter_by(college=college_filter)
    if gender_filter:
        query = query.filter_by(gender=gender_filter)

    matches = []
    for potential_match in query.all():
        try:
            match_percentage = calculate_match_percentage(current_user, potential_match)
        except (AttributeError, TypeError, ValueError) as e:
            print(f"Error calculating match for user {potential_match.id}: {e}")
            match_percentage = 0

        matches.append({
            'id': potential_match.id,
            'fullname': potential_match.fullname,
            'bio': potential_match.bio,
            'mobile_number': potential_match.mobile_number,
            'match_percentage': match_percentage,
            # Add more attributes as needed (e.g., college, gender, age)
            'college': potential_match.college, 
            'gender': potential_match.gender,
            'age': potential_match.age,
            
        })

    return jsonify({'matches': matches})



def calculate_match_percentage(user1, user2):
    match_score = 0
    max_score = 10  # Maximum possible score

    # 1. Gender Preference Matching (Weight: 3)
    if user1.interested_in == user2.gender or user1.interested_in == "Everyone":
        match_score += 3

    # 2. Age Range Compatibility (Weight: 2)
    age_difference = abs(user1.age - user2.age)
    if age_difference <= 5:  # Within 5 years
        match_score += 2
    elif age_difference <= 10:  # Within 10 years
        match_score += 1

    # 3. College Matching (Weight: 2)
    if user1.college and user2.college and user1.college.lower() == user2.college.lower():
        match_score += 2

    # 4. Field of Study Matching (Weight: 1)
    if user1.field_of_study and user2.field_of_study and user1.field_of_study.lower() == user2.field_of_study.lower():
        match_score += 1

    # 5. Interest Matching (Weight: 2)
    if user1.interests and user2.interests:
        user1_interests = set(user1.interests.lower().split(','))
        user2_interests = set(user2.interests.lower().split(','))
        common_interests = user1_interests.intersection(user2_interests)
        match_score += min(2, len(common_interests))  # Max 2 points for interests

    # Calculate match percentage
    match_percentage = (match_score / max_score) * 100
    return round(match_percentage)  # Round to nearest integer

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    current_user = User.query.get(session['user_id'])
    questions = [
        "Hi there! What's your name?",
        "Nice to meet you! What's your gender?",
        "Got it! How old are you?",
        "Where do you go to college?",
        "What's your field of study?",
        "When are you looking to move in? (YYYY-MM-DD)",  # Assuming you want move-in date as a date object
        "Tell us a bit about yourself and your ideal flatmate.",
        "Please enter your mobile number (with country code):"
    ]

    if request.method == 'POST':
        user_data = request.get_json()

        if user_data:
            for question, answer in user_data.items():
                if answer: # Ignore empty answers
                    if question == "Hi there! What's your name?":
                        current_user.fullname = answer
                    elif question == "Nice to meet you! What's your gender?":
                        current_user.gender = answer
                    elif question == "Got it! How old are you?":
                        try:
                            current_user.age = int(answer)
                        except ValueError:
                            flash('Invalid age. Please enter a number.', 'error')
                            return redirect(url_for('profile'))
                    elif question == "Where do you go to college?":
                        current_user.college = answer
                    elif question == "What's your field of study?":
                        current_user.field_of_study = answer
                    elif question == "When are you looking to move in? (YYYY-MM-DD)":
                        try:
                            current_user.move_in_date = datetime.strptime(answer, '%Y-%m-%d').date()
                        except ValueError:
                            flash('Invalid move-in date format. Please use YYYY-MM-DD.', 'error')
                            return redirect(url_for('profile'))
                    elif question == "Tell us a bit about yourself and your ideal flatmate.":
                        current_user.bio = answer
                    elif question == "Please enter your mobile number (with country code):":
                        current_user.mobile_number = answer

            try:
                db.session.commit()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('board'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred while updating your profile: {e}', 'error')
                return redirect(url_for('profile'))  # Redirect back to the profile page on error

    return render_template('profile.html', current_user=current_user, questions=questions)


# ... (rest of your code) ...


if __name__ == '__main__':
    app.run(debug=True)