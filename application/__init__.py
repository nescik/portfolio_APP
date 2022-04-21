from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager
from flask_migrate import Migrate
from flask_mail import Mail

app = Flask(__name__)


app.config.from_pyfile("config.cfg")
db = SQLAlchemy(app)

migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

from application import routes