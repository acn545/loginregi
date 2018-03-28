from flask import Flask, request, redirect, render_template, session, flash
import re
from mysqlconnection import MySQLConnector
import md5
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
mysql = MySQLConnector(app, 'register')
app.secret_key = "this is a secret key"
@app.route('/')
def index():
    session['email'] = ""
    query = "SELECT * FROM users"
    register = mysql.query_db(query)
    if len(session['email']) > 0 :
        return redirect('/dashboard')
    else:
        return render_template('index.html', regiseter = register)

@app.route('/log', methods=['POST'])
def loggin():
    if len(request.form['email']) < 1 or not EMAIL_REGEX.match(request.form['email']):
        flash('Please enter a valid email address')
        return redirect('/')
    elif len(request.form['password']) < 1:
        flash('please enter a password')
        return redirect('/')
    else:
        hashed_password = md5.new(request.form['password']).hexdigest()
        session['email'] = request.form['email']
        data = {
            'email': request.form['email'],
            'password': hashed_password
        }
        query ="SELECT * FROM users WHERE email = :email and password = :password"
        users = mysql.query_db(query,data)
        if len(users) > 0:
            user = users[0]
            if user['password'] == hashed_password:
                session['email'] = user['email']
                return redirect('/dashboard')
    flash('login failed try again')
    return redirect('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['POST'])
def register():
    return render_template('register.html')

@app.route('/regist', methods=['POST'])
def regist():
    form = request.form
    if len(form['first_name']) < 0 or len(form['last_name']) < 0:
        flash("Please enter a valid name")
        return redirect('/register')
    elif len(form['email']) < 0 or not EMAIL_REGEX.match(form['email']):
        flash("please enter a valid email address")
        return redirect('/register')
    elif form['password'] != form['cpassword']:
        flash('passwords do not match')
        return redirect('/register')
    else:
        hashed_password = md5.new(request.form['password']).hexdigest()
        query = "INSERT INTO `users` ( `email`, `password`, `first_name`, `last_name`, `created_at`, `updated_at`) VALUES (:email, :password, :first_name, :last_name, NOW(), NOW());"
        data = {
            "first_name": form['first_name'],
            "last_name": form['last_name'],
            "email": form['email'],
            "password": hashed_password

        }
        mysql.query_db(query, data)
    return render_template('dashboard.html')

app.run(debug=True)