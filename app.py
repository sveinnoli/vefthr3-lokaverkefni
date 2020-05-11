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

def add_cards(title, name, price, clockspeed, architecture):
    db.child("account").child(session["user_session"]["user_id"]).child("cards").push({"title":title, "name":name, "price":price, "clockspeed":clockspeed, "architecture":architecture})

def get_cards():
    return db.child("account").child(session["user_session"]["user_id"]).child("cards").get().val()

def find_card(card_id):
    return db.child("account").child(session["user_session"]["user_id"]).child("cards").child(card_id).get().val()

def update_card(title, name, price, clockspeed, architecture, card_id):#add variables that were changed
    db.child("account").child(session["user_session"]["user_id"]).child("cards").child(card_id).update({"title":title, "name":name, "price":price, "clockspeed":clockspeed, "architecture":architecture})


def remove_card(card_id):
    db.child("account").child(session["user_session"]["user_id"]).child("cards").child(card_id).remove()


@app.route('/')
def index():
    if in_session():
        return redirect(url_for('cards'))
    else:
        return redirect('signup')

#-----------------Sign up-----------------
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
        return redirect(url_for("cards"))
    else:
        if request.method == 'POST' and "username" in request.form:
            username = request.form['username']
            password = request.form['password']
            if login_check(username, password) != False:
                session["user_session"] = login_check(username,password)
                return redirect(url_for("cards"))
            else:
                error = "Invalid credentials"
        return render_template("login.html", error=error)

#-----------------Logout-----------------      
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if in_session() == True:
        session.pop("user_session", None)
    return redirect(url_for("login"))

#-----------------Product site-----------------
@app.route('/cards', methods=['POST', 'GET'])
def cards():
    if in_session() == True:
        if request.method == 'POST':
            if "remove" in request.form:
                card_id = request.form["remove"]
                remove_card(card_id)
                return redirect(url_for("cards"))
            elif "edit" in request.form:
                card_id = request.form["edit"]
                return redirect(url_for("edit"))
        return render_template("cards.html", cards=get_cards())
    return(render_template("403.html"), 403)

@app.route('/cards/create', methods=['POST', 'GET'])
def create():
    if in_session() == True:
        if request.method == 'POST' and len(request.form) > 1: #Bug with buttons that returns an empty ODICT and then returns all items 
            title = request.form['title']
            name = request.form['name']
            price = request.form['price']
            clockspeed = request.form['clockspeed']
            architecture = request.form['architecture']
            add_cards(title, name, price, clockspeed, architecture)
            return redirect(url_for('cards'))
        return render_template("create.html")
    return(render_template("403.html"), 403)

@app.route('/cards/<card_id>/edit', methods=['POST', 'GET'])
def edit(card_id):
    if in_session() == True:
        if request.method == 'POST' and len(request.form) > 1:
            title = request.form['title']
            name = request.form['name']
            price = request.form['price']
            clockspeed = request.form['clockspeed']
            architecture = request.form['architecture']
            update_card(title, name, price, clockspeed, architecture, card_id)
            return redirect(url_for("cards"))
        return render_template('edit.html', card_id=card_id, card=find_card(card_id))
    return(render_template("403.html"), 403)

@app.errorhandler(403)
def access_denied(e):
    return render_template("403.html"), 403

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('cards'))
if __name__ == "__main__":
	app.run(debug=True)

