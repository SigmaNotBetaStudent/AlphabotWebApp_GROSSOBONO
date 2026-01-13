from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required, 
    logout_user, current_user
)
import sqlite3
from werkzeug.security import check_password_hash
import Alphabot

app = Flask(__name__)
app.secret_key = 'chiave segreta'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

robot = Alphabot.AlphaBot()

# Classe User per Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Funzione per connessione al database
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

# Route di login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = verify_user(username, password)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Username o password non corretti', 'error')
    
    return render_template('login.html')

# Route di logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route principale con joystick
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Gestione comandi dal joystick
        if 'Avanti' in request.form:
            robot.forward()
        elif 'Indietro' in request.form:
            robot.backward()
        elif 'Sinistra' in request.form:
            robot.left()
        elif 'Destra' in request.form:
            robot.right()
        elif 'Stop' in request.form:
            robot.stop()
        
        return '', 204  # Risposta vuota per chiamate AJAX
    
    return render_template('index.html', username=current_user.username)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)