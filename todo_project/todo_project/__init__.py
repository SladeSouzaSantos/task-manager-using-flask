import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'uma-chave-secreta-padrao-de-dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login' 
login_manager.login_message_category = 'danger'

bcrypt = Bcrypt(app)

# Register Prometheus metrics endpoint
from .metrics import register_metrics, init_business_metrics
register_metrics(app)

# Ensure the database tables exist and initialise business metrics inside the app context.
# This prevents OperationalError when the container starts before the DB schema is created.
with app.app_context():
	# Create tables if they do not exist yet
	db.create_all()
	# Populate gauges/counters with the current DB state (run once at startup)
	init_business_metrics()

# Always put Routes at end
from todo_project import routes