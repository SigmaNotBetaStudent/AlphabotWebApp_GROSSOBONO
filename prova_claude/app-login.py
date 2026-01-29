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

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

def get_db_connection():
    conn = sqlite3.connect('utenze.db')
    conn.row_factory = sqlite3.Row
    return conn

# Carica l'utente dal database
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM Utenze WHERE Id = ?', (user_id,)).fetchone()
    conn.close()
    if user_data:
        return User(user_data['Id'], user_data['User'])
    return None

# Verifica credenziali
def verify_user(username, password):
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM Utenze WHERE User = ?', (username,)).fetchone()
    conn.close()
    
    if user_data:
        # Se le password sono in chiaro nel DB (non consigliato in produzione)
        if user_data['Psw'] == password:
            return User(user_data['Id'], user_data['User'])
        # Se le password sono hashate
        # if check_password_hash(user_data['Psw'], password):
        #     return User(user_data['Id'], user_data['User'])
    return None

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = verify_user(username, password)
        
        if user:
            login_user(user)
            flash(f"Benvenuto {username}!", "success")
            return redirect(url_for("control"))
        else:
            flash("Credenziali non valide!", "error")
    
    return render_template("login.html")

@app.route("/index")
@login_required
def control():
    return render_template("index.html", username=current_user.username)

# Nuova route per controllare i motori con il joystick
@app.route("/joystick", methods=["POST"])
@login_required
def joystick_control():
    try:
        data = request.get_json()
        x = float(data.get('x', 0))
        y = float(data.get('y', 0))
        
        max_joy = 85.0
        x_norm = -(x / max_joy) * 100
        y_norm = -(y / max_joy) * 100
        
        left_speed = y_norm + x_norm
        right_speed = y_norm - x_norm
        
        right_speed = max(-100, min(100, right_speed))
        left_speed = max(-100, min(100, left_speed))
        
        robot.setMotor(left_speed, right_speed)
        
        return jsonify({
            'success': True,
            'left': round(left_speed, 1),
            'right': round(right_speed, 1)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

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