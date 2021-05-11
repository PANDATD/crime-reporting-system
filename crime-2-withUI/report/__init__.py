import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager , current_user 

 

app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

app.config['SECRET_KEY'] = 'v658734657543276kreg'#emailpassword @crime.report.ghule.gmail.com
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['REMEMBER_COOKIE_DURATION'] = 1800
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.session_protection = "strong"
# login_manager.login_message = u"Please Login to use this page."
# login_manager.REMEMBER_COOKIE_HTTPONLY = True



from report import routes