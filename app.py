from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:VtcUICkrCjgHdudKRsNkEXMKUzNVzOca@monorail.proxy.rlwy.net:32903/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Replace with your secret key
db = SQLAlchemy(app)
migrate = Migrate(app, db)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    fullname = db.Column(db.String(120))
    gender = db.Column(db.String(10))
    age = db.Column(db.String(10))
    college = db.Column(db.String(120))
    stream = db.Column(db.String(120))
    move_in = db.Column(db.String(20))
    year = db.Column(db.String(10))
    notes = db.Column(db.Text)
    society = db.Column(db.String(120))
    profile_photo = db.Column(db.String(120))  # New column for profile photo URL

    def __repr__(self):
        return '<User %r>' % self.username
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

# Route to update user profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Retrieve form data
        fullname = request.form.get('fullname')
        gender = request.form.get('gender')
        age = request.form.get('age')
        college = request.form.get('college')
        stream = request.form.get('stream')
        move_in = request.form.get('move_in')
        year = request.form.get('year')
        notes = request.form.get('notes')
        society = request.form.get('society')

        # Update user's profile in the database
        current_user = User.query.get(session['user_id'])
        current_user.fullname = fullname
        current_user.gender = gender
        current_user.age = age
        current_user.college = college
        current_user.stream = stream
        current_user.move_in = move_in
        current_user.year = year
        current_user.notes = notes
        current_user.society = society

        # Commit changes to the database
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('board'))  # Redirect to board page after update

    # Fetch current user's profile data
    current_user = User.query.get(session['user_id'])
    return render_template('profile.html', current_user=current_user)


if __name__ == '__main__':
    app.run(debug=True)