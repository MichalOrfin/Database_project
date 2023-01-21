from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Email,EqualTo
from forms import RegistrationForm, LoginForm
from models import User, Player
# import templates
from templates import *

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


login_manager = LoginManager()
login_manager.init_app(app)
@app.route("/")
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/register', methods = ['POST','GET'])
def register():
    form = RegistrationForm()
    # if form.validate_on_submit():
    #     user = User(username =form.username.data, email = form.email.data)
    #     user.set_password(form.password1.data)
    #     db.session.add(user)
    #     db.session.commit()
    #     return redirect(url_for('login'))
    return render_template('registration.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # if form.validate_on_submit():
        # user = User.query.filter_by(email = form.email.data).first()
        # if user is not None and user.check_password(form.password.data):
        #     login_user(user)
        #     next = request.args.get("next")
        #     return redirect(next or url_for('home'))
        # flash('Invalid email address or Password.')    
    return render_template('login.html', form=form)

@app.route('/players', methods=['GET'])
def players_list():
    # players = [Player.load(db, uid) for uid in db]
    players = ['Dupa', 'Twoja stara']
    return render_template('players_list.html', players=players)

#show team
#create user
    #100m to spend
#choose player
    #2 goalkeeper
    #5 defenders
    #5 midfilders
    #3 offensives
    #check if money available
#change player
