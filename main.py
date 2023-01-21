from flask import Flask, redirect, url_for, render_template
# from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Email,EqualTo
from forms import RegistrationForm, LoginForm
from models import User, Player
# import templates
from templates import *
import sqlite3

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

connection = sqlite3.connect('fpl_v2.db', check_same_thread=False)
cursor = connection.cursor()

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/")
def logres():
    return render_template('logres.html')

@app.route("/index")
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/register', methods = ['POST','GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(login =form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        cursor.execute(f'insert into users values (1,"{user.login}", "{user.email}", "{user.password}")')
        return redirect(url_for('login'))
    return render_template('registration.html', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
     cursor.execute("SELECT id, email FROM users where email = (?)",    [form.email.data])
     user = list(curs.fetchone())
     Us = load_user(user[0])
     if form.email.data == Us.email and form.password.data == Us.password:
        login_user(Us, remember=form.remember.data)
        Umail = list({form.email.data})[0].split('@')[0]
        flash('Logged in successfully '+Umail)
        redirect(url_for('profile'))
     else:
        flash('Login Unsuccessfull.')
  return render_template('login.html',title='Login', form=form)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     # if form.validate_on_submit():
#         # user = User.query.filter_by(email = form.email.data).first()
#         # if user is not None and user.check_password(form.password.data):
#         #     login_user(user)
#         #     next = request.args.get("next")
#         #     return redirect(next or url_for('home'))
#         # flash('Invalid email address or Password.')    
#     return render_template('login.html', form=form)

@app.route('/players/<string:pos>', methods=['GET'])
def players_list(pos):
    print('DUPA')
    print(pos)
    # players = [Player.load(db, uid) for uid in db]
    cursor.execute( F"""select gw1.name, gw1.team, gw1.value, gw2.total_points, gw2.goals_scored, gw2.assists, gw2.clean_sheets FROM
 (select distinct name, team, round(value*0.1, 1) as value from merged_gw where gw=20 and position = "{pos}") gw1
 JOIN
 (select name, sum(total_points) as total_points, sum(goals_scored) as goals_scored,
sum(assists) as assists, sum(clean_sheets) as clean_sheets
from merged_gw where GW is not NULL group by name) gw2
on gw1.name=gw2.name
order by gw2.total_points desc, gw1.value desc""")
    players = cursor.fetchall()
    print(players)
    return render_template('players_list.html', players=players)

@app.route('/roles', methods=['GET'])
def roles():
    return render_template('roles.html')

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
