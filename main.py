from msilib.schema import AdminExecuteSequence
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import re
from collections import defaultdict
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = r"C:\Users\dhana\coding\Personal Projects\Web-Portal\static\Images"


db = SQLAlchemy(app)

app.secret_key = "Not Defined yet"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# print statements for personal understandings

# Login
class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Admin Login
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    
# Add to Cart
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False)
    variety = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    
class AdminItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.Integer, nullable=False)
    item_quantity = db.Column(db.Integer, nullable=False)
    item_price = db.Column(db.Integer, nullable=False)
    item_image = db.Column(db.String(255),nullable=False)

@app.route("/", methods=['GET'])
def start():
    return render_template('startpage.html')

# adding the admin in db
'''
admin = Admin(first_name='dhananjay', last_name='pai', email='dhananjay2002pai@gmail.com', password='123456')
db.session.add(admin)
db.session.commit()
'''

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    msg = ""
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        usr = Admin.query.filter_by(email=email).first()
        if not usr:
            msg = "Email does not exist"
            return render_template('adminlogin.html',msg=msg)
        if usr.password!=password:
            msg = "Entered wrong password"
            return render_template('adminlogin.html',msg=msg)
        msg = "Logged in Successfully"
        session['adminlogin'] = True
        session['id'] = usr.id
        session['adminemail'] = usr.email
        return redirect(url_for('adminhome'))
    if session.get('adminlogin'):
        return redirect(url_for('adminhome'))
    return render_template('adminlogin.html',msg=msg)

@app.route("/adminhome", methods=['GET', 'POST'])
def adminhome():
    msg = ""
    if session['adminlogin']:
        return render_template('adminhome.html')
    return redirect(url_for('admin'))
        
@app.route('/adminlogout', methods=['GET', 'POST'])
def alogout():
    session.pop('adminlogin', None)
    session.pop('id', None)
    session.pop('adminemail', None)
    return redirect(url_for('admin'))

@app.route("/home", methods=['GET', 'POST'])
def home():
    
    if 'loggedin' in session:
        return redirect(url_for('home'))
    return render_template('loginpage.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        entered_fname = request.form.get('firstname')
        entered_lname = request.form.get('lastname')
        entered_email = request.form.get('email')
        entered_pass = request.form.get('password')
        entered_cpass = request.form.get('password-confirm')
        print(entered_fname, entered_lname, entered_email, entered_pass, entered_cpass)
        if not entered_fname or not entered_lname or not entered_email or not entered_pass or not entered_cpass:
            msg = 'empty field'
            return render_template('signup.html',msg=msg)
        if entered_pass != entered_cpass:
            msg = 'entered password and confirmed password does not match'
            return render_template('signup.html',msg=msg)
        check = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        validity = re.fullmatch(check, entered_email)
        if not validity:
            msg = 'Please Enter a valid email address'
            return render_template('signup.html',msg=msg)
        email_exists = Login.query.filter_by(email=entered_email).all()
        if email_exists:
            msg ='Email already exists'
            return render_template('signup.html',msg=msg)
        new_user = Login(first_name=entered_fname, last_name=entered_lname, email=entered_email, password=entered_pass)
        db.session.add(new_user)
        db.session.commit()
        msg = 'registered successfully'
    return render_template('signup.html',msg=msg)
        
        
@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        entered_email = request.form.get('email')
        entered_pass = request.form.get('password')
        print(entered_email, entered_pass)
        if not entered_email or not entered_pass:
            msg = 'Please Enter your email and password'
            return render_template('loginpage.html',msg=msg)
        user = Login.query.filter_by(email=entered_email).first()
        if not user:
            msg = 'Email does not exist'
            return render_template('signup.html',msg=msg)
        print(user.password, entered_pass)
        if user.password!=entered_pass:
            msg = 'Email or password incorrect'
            return render_template('loginpage.html',msg=msg)
        msg = 'Logged in Successfully'
        session['loggedin'] = True
        session['id'] = user.id
        session['email'] = user.email
        return render_template('index.html',msg=msg)
        
    return render_template('loginpage.html',msg=msg)

@app.route("/admin/view", methods=['GET', 'POST'])
def view():
    if session.get('adminlogin'):
        all_data = AdminItems.query.all()
        
        data = defaultdict(list)
        for i in all_data:
            data[i.id] = [i.item_name,i.item_quantity,i.item_price]
        print(data)
        return render_template('adminview.html',data=data)
    return redirect(url_for('admin'))

@app.route("/admin/add", methods=['GET', 'POST'])
def add():
    msg = ""
    if session.get('adminlogin'):
        if request.method=='POST':
            file = request.files.get('image')
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
            file.save(file_path)
            print('image saved')
            pname = request.form.get('pname')
            pquantity = request.form.get('pquantity')
            pquantity = int(pquantity)
            pprice = request.form.get('pprice')
            pprice = int(pprice)
            print(pname,pquantity,pprice,file_path)
            
            product = AdminItems(item_name=pname,item_quantity=pquantity,item_price=pprice,item_image=file_path)
            db.session.add(product)
            db.session.commit()
            print('saved')
            msg = 'Item added Successfully'
            return render_template('adminadd.html', msg=msg)
        return render_template('adminadd.html',msg=msg)
    return redirect(url_for('admin'))

@app.route("/admin/update", methods=['GET', 'POST'])
def update():
    if session.get('adminlogin'):
        return render_template('adminupdate.html ')
    return redirect(url_for('admin'))

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    msg = "Logged out Successfully"
    print(session)
    return redirect(url_for('login'))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    return render_template('cart.html')

@app.route("/almond", methods=['GET', 'POST'])
def almond():
    return render_template('almond.html')

@app.route("/kaju", methods=['GET', 'POST'])
def kaju():
    return render_template('kaju.html')


if __name__=="__main__":
    app.run(debug=True)