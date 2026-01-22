# from flask import Flask, render_template, redirect, url_for, request, flash
# from flask_login import (
#     LoginManager, UserMixin,
#     login_user, login_required, 
#     logout_user, current_user
# )
# import sqlite3
# import Alphabot

# app = Flask(__name__)
# app.secret_key = 'chiave segreta'

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# robot = Alphabot.AlphaBot()
# class User(UserMixin):
#     def __init__(self, id):
#         self.id = id
#     USERS = {

#     }

# def load_user(user, id):
#     if user_id in USERS:
#         return User(user_id)
#     return None

# # da fare def load_user():
# @app.route("/", methods=["GET", "POST"])
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method =="POST":
#         username = request.form.get("username")
#         password = request.form.get("password")
#         #query = "SELECT * FROM Utenze WHERE User = ? AND Psw = ?"
#         if username in USERS and USERS[username]["password" ] == password:
#             login_user(User(username))
#             return redirect(url_for("control"))

#     return render_template("login.html")
# @app.route("/control")
# @login_required
# def control():
#     return render_template("control.html")

# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for("login"))
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required, 
    logout_user, current_user
)
import AlphaBot
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = 'chiave_segreta_molto_piu_sicura_cambiala!'  # Cambia questa chiave!

# Inizializzazione Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#DB
nomeDB="utenze.db"

robot = AlphaBot.AlphaBot()
robot.stop()

class User(UserMixin):
    def __init__(self, id):
        self.id = id

def dbDictionaryPopulator():
    con = sql.connect(nomeDB)
    cur = con.cursor()
    risultati = cur.execute(f"SELECT User, Psw FROM Utenze").fetchall()

    for username, password in risultati:
            USERS[username] = {"password": password}
    return True

USERS = {}
dbDictionaryPopulator()


@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(user_id)
    return None

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username in USERS and USERS[username]["password"] == password:
            login_user(User(username))
            flash(f"Benvenuto {username}!", "success")
            return redirect(url_for("control"))
        else:
            flash("Credenziali non valide!", "error")
    
    return render_template("login.html")

@app.route("/index", methods=["GET", "POST"])
@login_required
def control():
    if request.method == "POST":
        if "Avanti" in request.form:
            robot.forward()
        elif "Indietro" in request.form:
            robot.backward()
        elif "Destra" in request.form:
            robot.right()
        elif "Sinistra" in request.form:
            robot.left()
        elif "Stop" in request.form:
            robot.stop()
        
        return render_template("index.html", username=current_user.id)
    
    return render_template("index.html", username=current_user.id)

# Route di logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout effettuato con successo!", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")


