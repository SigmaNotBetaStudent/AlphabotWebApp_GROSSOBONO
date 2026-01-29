from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required, 
    logout_user, current_user
)
import AlphaBot
import sqlite3

app = Flask(__name__)
app.secret_key = 'EliaSanMauroSkibidi'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

robot = AlphaBot.AlphaBot()
robot.stop()

# Nome del database
DB_NAME = 'utenze.db'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

def get_db_connection():
    """Restituisce una connessione al database"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_username(username):
    """Recupera un utente dal database tramite username"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Utenze WHERE User = ?', (username,)).fetchone()
    conn.close()
    return user

def add_user(username, password):
    """Aggiunge un nuovo utente al database"""
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO Utenze (User, Psw) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Username già esistente

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Utenze WHERE Id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        return User(user['Id'], user['User'])
    return None

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = get_user_by_username(username)
        
        if user and user['Psw'] == password:
            user_obj = User(user['Id'], user['User'])
            login_user(user_obj)
            flash(f"Benvenuto {username}!", "success")
            return redirect(url_for("control"))
        else:
            flash("Credenziali non valide!", "error")
    
    return render_template("login.html")

@app.route("/index")
@login_required
def control():
    return render_template("index.html", username=current_user.username)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Route per registrare un nuovo utente"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username and password:
            if add_user(username, password):
                flash(f"Utente {username} registrato con successo!", "success")
                return redirect(url_for("login"))
            else:
                flash("Username già esistente!", "error")
        else:
            flash("Compila tutti i campi!", "error")
    
    return render_template("register.html")

@app.route("/joystick", methods=["POST"])
@login_required
def joystick_control():
    data = request.get_json()
    x = float(data.get('x', 0))
    y = float(data.get('y', 0))

    max_joy = 85.0

    # Scambio assi + inversione corretta
    turn = (y / max_joy) * 100
    forward = -(x / max_joy) * 100

    left_speed = forward + turn
    right_speed = forward - turn

    left_speed = max(-100, min(100, left_speed))
    right_speed = max(-100, min(100, right_speed))

    robot.setMotor(left_speed, right_speed)

    return jsonify({
        'success': True,
        'left': round(left_speed, 1),
        'right': round(right_speed, 1)
    })
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout effettuato con successo!", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    try:
        app.run(debug=False, host="0.0.0.0")
    finally:
        robot.stop()
        GPIO.cleanup()