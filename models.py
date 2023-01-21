from flask_login import UserMixin
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
# from main import db

class User(UserMixin):
  id = ''
#   id = db.Column(db.Integer, primary_key=True)
#   username = db.Column(db.String(50), index=True, unique=True)
#   email = db.Column(db.String(150), unique = True, index = True)
#   password_hash = db.Column(db.String(150))
#   joined_at = db.Column(db.DateTime(), default = datetime.utcnow, index = True)
    # access = db.Column(db.Integer) 0-user, 1-dev, 2-admin
    #available_money

  def set_password(self, password):
        self.password_hash = generate_password_hash(password)

  def check_password(self,password):
      return check_password_hash(self.password_hash,password)

class Player():
    id = ''
    name = ''
    surname = ''
    goals = 0
    assists = 0
    clean_sheets = 0
    yellow_cards = 0
    red_cards = 0
    minutes = 0
    total_points = 0
    value = 0
