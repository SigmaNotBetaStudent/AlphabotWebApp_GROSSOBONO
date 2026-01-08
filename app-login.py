from flask import Flask, render_template, redirect, url_for, request
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required, 
    logout_user, current_user
)
import Alphabot

app = Flask(__name__)

app.secret_key = 'chiave segreta'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

robot = Alphabot()