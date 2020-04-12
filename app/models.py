from app import app, db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique = True)
    password = db.Column(db.String(128), unique=False)

    def __repr__(self):
        return '<user {}>'.format(self.username)
        
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_id(self):
        return self.user_id

class Post(UserMixin, db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    subtitle = db.Column(db.String(64))
    raw_body = db.Column(db.String())
    tags = db.Column(db.String())
    date = db.Column(db.String(64))

    def get_id(self):
        return self.post_id

class Messages(UserMixin, db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    email = db.Column(db.String(64))
    phone = db.Column(db.String(16))
    message = db.Column(db.String(128))

@login.user_loader
def load_user(id):
   return User.query.get(int(id))