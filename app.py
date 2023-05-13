from flask import Flask, render_template, request, redirect, url_for
import db_functions as dbf

app = Flask(__name__)
logged_in_username = ""


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    global logged_in_username

    email = request.form['email']
    password = request.form['password']

    logged_in_username = dbf.validate_user(email, password)

    if logged_in_username != "":
        return redirect(url_for('home'))

    else:
        return render_template('login.html', message='Invalid Gmail or Password, Please Try Again')


@app.route('/sign-up')
def sign_up():
    return render_template('sign_up.html')


@app.route('/store-user', methods=['GET', 'POST'])
def store_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    dbf.sign_up_user(username, email, password)

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logged_in_username = ""

    return render_template('login.html', message='Successfully Logged Out!')