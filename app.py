import os, pyrebase
from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)

#Session key
app.config['SECRET_KEY'] = os.urandom(16).hex()

config = {
    "apiKey": "AIzaSyDDcL0pFjECQ-0j-1hgPFwLFrMnrUVT5SQ",
    "authDomain": "vefthr3-firebase.firebaseapp.com",
    "databaseURL": "https://vefthr3-firebase.firebaseio.com",
    "projectId": "vefthr3-firebase",
    "storageBucket": "vefthr3-firebase.appspot.com",
    "messagingSenderId": "459938427281",
    "appId": "1:459938427281:web:7b80b54378cc611a6dea30",
    "measurementId": "G-T1M5ZMHXXF"
}

fb = pyrebase.initialize_app(config)
db = fb.database()
userbase = db.child("account").get().val() 

if userbase == None: # Avoids crashing if db is empty
    userbase = {}
    
def signup_check(username):
    newbase = db.child("account").get().val()
    for key,value in newbase.items():
        if value["username"] == username:
            return False
    return True

def login_check(username, password):
    userData = {}
    newbase = db.child("account").get().val()
    for key, value in newbase.items():
        if value["username"] == username and value["password"] == password:
            userData["username"] = username
            userData["password"] = password 
            userData["user_id"] = key
            return userData
    return False

def in_session():
    newbase = db.child("account").get().val()
    if "user_session" in session:
        for key, value in newbase.items():
            if value["username"] == session["user_session"]["username"] and value["password"] == session["user_session"]["password"]:
                return True
    return False

@app.route('/')
def index():
    if in_session():
        return redirect(url_for('products'))
    else:
        return redirect('signup*')

#-----------------Sign up-----------------
#Maybe rename signup to account or something of the sort
@app.route('/signup', methods=['GET','POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if signup_check(username) == False:
            error = 'User already exists, try again.'
        elif signup_check(username) == True:
            db.child("account").push({"username":username, "password":password})
            return redirect(url_for('login'))
    return render_template("signup.html", error=error)  

#-----------------Login-----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if in_session() == True:
        return redirect(url_for("products"))
    else:
        if request.method == 'POST' and "username" in request.form:
            username = request.form['username']
            password = request.form['password']
            if login_check(username, password) != False:
                session["user_session"] = login_check(username,password)
                return redirect(url_for("products"))
            else:
                error = "Invalid credentials"
        return render_template("login.html", error=error)

#-----------------Logout-----------------      
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if in_session() == True:
        session.pop("user_session", None)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

#-----------------Product site-----------------
@app.route('/products', methods=['POST', 'GET'])
def products():
    name = None
    if in_session() == True:
        name = session["user_session"]["username"]
        if request.method == 'POST':
            if "user_session" in session:
                session.pop("user_session", None)
                return redirect(url_for("login"))
        return render_template("products.html", name=name)
    return(render_template("403.html"), 403)

@app.errorhandler(403)
def access_denied(e):
    return render_template("403.html"), 403

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('products'))
if __name__ == "__main__":
	app.run(debug=True)

