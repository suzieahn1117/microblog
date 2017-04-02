from flask import Flask
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

app.config['OAUTH_CREDENTIALS'] = {
	'facebook': {
		'id': '1898096913799943',
		'secret': 'bdcb1375ce940945185b71fd1d929b13'
	}
}

db = SQLAlchemy(app)
lm = LoginManager(app)


db.create_all()
from app import views, models