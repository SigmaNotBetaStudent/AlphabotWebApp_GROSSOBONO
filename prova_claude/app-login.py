from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required, 
    logout_user, current_user
)
import AlphaBot

app = Flask(__name__)
app.secret_key = 'chiave_segreta_molto_piu_sicura_cambiala!'

# Inizializzazione Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

robot = AlphaBot.AlphaBot()
robot.stop()

class User(UserMixin):
    def __init__(self, id):
        self.id = id

USERS = {
    "admin": {"password": "admin123"},
    "utente1": {"password": "password1"}
}

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

@app.route("/index")
@login_required
def control():
    return render_template("index.html", username=current_user.id)

# Nuova route per controllare i motori con il joystick
@app.route("/joystick", methods=["POST"])
@login_required
def joystick_control():
    try:
        data = request.get_json()
        x = float(data.get('x', 0))
        y = float(data.get('y', 0))
        
        # Converti le coordinate del joystick in velocità dei motori
        # x: -85 a +85 (sinistra/destra)
        # y: -85 a +85 (avanti/indietro, negativo = avanti)
        
        # Normalizza i valori da -85/85 a -100/100
        max_joy = 85.0
        x_norm = -(x / max_joy) * 100  # Inverti X per correggere sinistra/destra
        y_norm = -(y / max_joy) * 100  # Inverti Y (negativo = avanti)
        
        # Calcola velocità motori con mixing
        # Motore sinistro (left): base + steering
        # Motore destro (right): base - steering
        left_speed = y_norm + x_norm
        right_speed = y_norm - x_norm
        
        # Limita i valori a -100/+100
        right_speed = max(-100, min(100, right_speed))
        left_speed = max(-100, min(100, left_speed))
        
        # Invia i comandi al robot
        robot.setMotor(left_speed, right_speed)
        
        return jsonify({
            'success': True,
            'left': round(left_speed, 1),
            'right': round(right_speed, 1)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Route di logout
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