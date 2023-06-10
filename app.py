from flask import Flask, render_template, request, redirect, url_for
import database_functions as dbf\

app = Flask(__name__)
current_user = " "

# ---------- Index ----------
@app.route('/')
def index():
    return render_template('login.html')


# ---------- Login/Signup ----------
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/verify-user", methods=['GET', 'POST'])
def verify_user():
    global current_user

    username = request.form['username']
    password = request.form['password']

    current_user = dbf.verify_user(username, password)

    if current_user != "":
        return redirect(url_for('home'))
    else:
        return render_template('login.html', message='Invalid Username or Password, Please Try Again')

@app.route('/store-user', methods=['GET', 'POST'])
def store_user():
    global current_user

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Returning blank means no information linked to username is found (aka username doesn't exist)
    if dbf.get_user_information(username)['username'] == "":
        dbf.signup_user(username, email, password)

        current_user = username

        return redirect(url_for('home'))

    else:
        return render_template('login.html', message="Email Already In Use, Log In Instead?")

@app.route('/logout')
def logout():
    global current_user

    current_user = ""

    return render_template('login.html', message='Successfully Logged Out!')


# ---------- Homepage ----------
@app.route("/home")
def home():
    global current_user

    message = ""

    if current_user != "":
        message = f"Hello there {current_user}! Welcome to Naruto RPG"

    return render_template("home.html", current_user=current_user, message=message)

# ---------- Battle ----------
# @app.route("/battle")
# def battle():


# ---------- Training ----------
# @app.route("/training")
# def training():

# ---------- Resources ----------
@app.route("/resources")
def resources():
    return render_template('resources.html')

# ----------  ----------
if __name__== '__main__':
    app.run(debug=True, host ='0.0.0.0', port = 9000)