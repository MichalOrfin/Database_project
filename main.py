from flask import Flask, redirect, url_for, render_template, flash, request, session
# from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Email,EqualTo
from forms import RegistrationForm, LoginForm
from models import User, Player
# import templates
from templates import *
import sqlite3
import json

app = Flask(__name__)
app.debug=True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

connection = sqlite3.connect('fpl_v2.db', check_same_thread=False)
# cursor = connection.cursor()

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/")
def logres():
    return render_template('logres.html')

@app.route("/index")
def index():
    return render_template('index.html')

# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)

@app.route('/register', methods = ['POST','GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        cursor = connection.cursor()
        max_id = cursor.execute('select max(id) from users').fetchone()[0]
        if not max_id:
            max_id = 0
        user = User(max_id+1, login =form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        connection.commit()
        cursor.execute(f'insert into users values ({max_id+1}, "{user.login}", "{user.password}", "{user.email}",{user.team_value})')
        connection.commit()
        # connection.commit()
        return redirect(url_for('login'))
    return render_template('registration.html', form=form)

@login_manager.user_loader
def load_user(user_id):
   curs = connection.cursor()
   curs.execute("SELECT * from users where id = (?)",[user_id])
   lu = curs.fetchone()
   if lu is None:
      return None
   else:
      return User(int(lu[0]), lu[1], lu[3])

@app.route("/login", methods=['GET','POST'])
def login():
  if current_user.is_authenticated:
     return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
     curs = connection.cursor()
     curs.execute("SELECT id FROM users where email = (?)",    [form.email.data])
     user =curs.fetchone()
    #  print(user)
     Us = load_user(user[0])
     if form.email.data == Us.email and Us.check_password(form.password.data, curs):
        login_user(Us, remember=form.remember.data)
        Umail = list({form.email.data})[0].split('@')[0]
        flash('Logged in successfully '+Umail)
        session['user'] = json.dumps(Us.__dict__)
        return redirect(url_for('index'))
     else:
        flash('Login Unsuccessfull.')
  return render_template('login.html',title='Login', form=form)

@app.route('/players/<string:pos>', methods=['GET'])
def players_list(pos):
    # players = [Player.load(db, uid) for uid in db]
    cursor = connection.cursor()
    cursor.execute( F"""select gw1.name, gw1.team, gw1.value, gw2.total_points, gw2.goals_scored, gw2.assists, gw2.clean_sheets FROM
 (select distinct name, team, round(value*0.1, 1) as value from merged_gw where gw=20 and position = "{pos}") gw1
 JOIN
 (select name, sum(total_points) as total_points, sum(goals_scored) as goals_scored,
sum(assists) as assists, sum(clean_sheets) as clean_sheets
from merged_gw where GW is not NULL group by name) gw2
on gw1.name=gw2.name
order by gw2.total_points desc, gw1.value desc""")
    players = cursor.fetchall()
    return render_template('players_list.html', players=players)

@app.route('/add_player', methods=['POST'])
def add_player():
    name = request.form.get('NAME')
    first_name = name.split(' ')[0]
    last_name = name.strip(first_name)[1:]
    cursor = connection.cursor()
    print(first_name)
    print(last_name)
    player_id = cursor.execute("select id from player_idlist where first_name = (?) and second_name = (?)", [first_name, last_name]).fetchone()[0]
    user = json.loads(session['user'])
    player_value = cursor.execute("select value from merged_gw where name = (?)", [name]).fetchone()[0]
    if int(user["team_value"]) + int(player_value) > 1000:
        return redirect(url_for("team", message = 'Not enough money to buy this player'))
    player_in_team = cursor.execute("select 1 from player_team where player_id = (?) and user_id = (?)", [player_id, user["id"]]).fetchone()

    if player_in_team:
        return redirect(url_for("team", message='Player already in team'))
    
    player_pos = cursor.execute("""select gw.position, count(gw.position) from player_team pt join player_idlist pil on pt.player_id = pil.id join merged_gw gw 
on gw.name = pil.first_name || " " || pil.second_name where gw.position = (select gw.position from player_idlist pil join merged_gw gw 
on gw.name = pil.first_name || " " || pil.second_name where pil.id = 1 and gw.GW= 20) and user_id = 1 and gw.GW= 20 group by gw.position""")
    player_pos = player_pos.fetchall()
    if player_pos:
        player_pos = player_pos[0]
        if player_pos[0] =='GK' :
            if player_pos[1] > 1:
                return redirect(url_for("team", message = "Alread have 2 goalkeepers"))
        if player_pos[0] == 'FWD':
            if player_pos[1] > 2: 
                return redirect(url_for("team", message = "Alread have 3 forwards"))
        if player_pos[0] == 'MID':
            if player_pos[1] > 4: 
                return redirect(url_for("team", message = "Alread have 5 midfielders"))
        if player_pos[0] == 'DEF':
            if player_pos[1] > 4: 
                return redirect(url_for("team", message = "Alread have 5 defenders"))
        #get player_value
    player_team = cursor.execute("""select gw.team, count(gw.team) from player_team pt join player_idlist pil on pt.player_id = pil.id join merged_gw gw 
on gw.name = pil.first_name || " " || pil.second_name where gw.position = (select gw.position from player_idlist pil join merged_gw gw 
on gw.name = pil.first_name || " " || pil.second_name where pil.id = 1 and gw.GW= 20) and user_id = (?) and gw.GW= 20 group by gw.team""", [user["id"]])
    player_team = player_team.fetchall()
    if player_team:
        player_team = player_team[0]
        if player_team[1] > 2:
            return redirect(url_for("team", message = "Too many players from one team"))

    cursor.execute("insert into player_team (user.id, player.id)", [])
    return redirect(url_for('team', message = 'Player added to your team'))


@app.route('/team', methods=['GET'])
def team():
    print(request.args)
    message = request.args['message']
    print(message)
    cursor = connection.cursor()
    cursor.execute("""select gw.name, gw.team, round(gw.value*0.1, 1), gw.total_points, gw.goals_scored, gw.assists, gw.clean_sheets from player_team pt join player_idlist pil on pt.player_id = pil.id join merged_gw gw 
on gw.name = pil.first_name || " " || pil.second_name where user_id = 1 and gw.GW= 20""")
    players = cursor.fetchall()
    print(players)
    return render_template('player_team.html', message=message, players=players)





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
