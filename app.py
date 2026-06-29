import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

FLW_SECRET_KEY = os.getenv("FLW_SECRET_KEY")
FLW_PUBLIC_KEY = os.getenv("FLW_PUBLIC_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-charity')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///preview.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

class GalleryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    media_url = db.Column(db.String(500), nullable=False)
    media_type = db.Column(db.String(10), default='image') # image or video

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Basic Routes
@app.route('/')
def index():
    projects = Project.query.limit(3).all()
    return render_template('index.html', projects=projects)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/mission-vision')
def mission_vision():
    return render_template('mission_vision.html')

@app.route('/programs')
def programs():
    projects = Project.query.all()
    return render_template('programs.html', projects=projects)

@app.route('/gallery')
def gallery():
    items = GalleryItem.query.all()
    return render_template('gallery.html', items=items)

# this is an addition 
@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        donor_name = request.form['donor_name']
        email = request.form['email']
        amount = request.form['amount']

        donation = Donation(
            donor_name=donor_name,
            email=email,
            amount=amount,
            transaction_id="TEMP-" + str(datetime.utcnow())
        )

        db.session.add(donation)
        db.session.commit()

        flash("Donation recorded successfully!", "success")

        return redirect(url_for('donation_success'))

    return render_template('donate.html')
# it ends here


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password: # In production, use password hashing
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/donation-success')
def donation_success():
    # Send email notification logic
    try:
        msg = Message("Thank you for your donation!",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[current_user.email if current_user.is_authenticated else "donor@example.com"])
        msg.body = "Your donation was successful. Thank you for supporting CharityOrg!"
        # mail.send(msg) # Uncomment in production with valid credentials
    except Exception as e:
        print(f"Email error: {e}")
    
    flash('Thank you for your generous donation!', 'success')
    return render_template('index.html')

#comparison
import requests
import uuid
from flask import request, redirect, url_for

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':

        donor_name = request.form['donor_name']
        email = request.form['email']
        amount = float(request.form['amount'])

        tx_ref = str(uuid.uuid4())

        headers = {
            "Authorization": f"Bearer {os.getenv('FLW_SECRET_KEY')}",
            "Content-Type": "application/json"
        }

        data = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": "USD",
            "redirect_url": url_for('donation_success', _external=True),
            "payment_options": "card,banktransfer,mobilemoneyuganda",
            "customer": {
                "email": email,
                "name": donor_name
            },
            "customizations": {
                "title": "CharityOrg Donation",
                "description": "Support NGO work"
            }
        }

        response = requests.post(
            "https://api.flutterwave.com/v3/payments",
            json=data,
            headers=headers
        )

        link = response.json()["data"]["link"]

        return redirect(link)

    return render_template("donate.html")

# end of donation model

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    donations = Donation.query.order_by(Donation.date.desc()).all()
    return render_template('admin/dashboard.html', donations=donations)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create a default admin user for preview
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', password='password123', is_admin=True)
            db.session.add(admin)
            db.session.commit()
    app.run(host='0.0.0.0', port=5000)

#env
   

