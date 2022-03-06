from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = "Not Defined yet"

# print statements for personal understandings

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)

@app.route("/")
def start():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/home", methods=['GET', 'POST'])
def home():
    print(session)
    if 'loggedin' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        entered_fname = request.form.get('firstname')
        entered_lname = request.form.get('lastname')
        entered_email = request.form.get('email')
        entered_pass = request.form.get('password')
        entered_cpass = request.form.get('password-confirm')
        print(entered_fname, entered_lname, entered_email, entered_pass, entered_cpass)
        if not entered_fname or not entered_lname or not entered_email or not entered_pass or not entered_cpass:
            print('empty field')
            return redirect(url_for('register'))
        if entered_pass != entered_cpass:
            print('cemail!=email')
            return redirect(url_for('register'))
        check = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        validity = re.fullmatch(check, entered_email)
        if not validity:
            print('email not proper')
            return redirect(url_for('register'))
        email_exists = Login.query.filter_by(email=entered_email).all()
        if email_exists:
            print('email already exists')
            return redirect(url_for('register'))
        new_user = Login(first_name=entered_fname, last_name=entered_lname, email=entered_email, password=entered_pass)
        db.session.add(new_user)
        db.session.commit()
        print('end')
        return redirect(url_for('login'))
    return render_template('signup.html')
        
        
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_email = request.form.get('email')
        entered_pass = request.form.get('password')
        print(entered_email, entered_pass)
        if not entered_email or not entered_pass:
            print('no email or pass')
            return redirect(url_for('login'))
        user = Login.query.filter_by(email=entered_email).first()
        if not user:
            print('no user with that email')
            return redirect(url_for('register'))
        print(user.password, entered_pass)
        if user.password==entered_pass:
            print('right credentials')
            session['loggedin'] = True
            session['id'] = user.id
            session['email'] = user.email
            return redirect(url_for('home'))
        
    return render_template('loginpage.html')

@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    print(session)
    return redirect(url_for('login'))

@app.route("/almond", methods=['GET', 'POST'])
def almond():
    return render_template('almond.html')

@app.route("/kaju", methods=['GET', 'POST'])
def kaju():
    return render_template('kaju.html')

if __name__=="__main__":
    app.run(debug=True)