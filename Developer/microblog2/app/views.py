from flask import Flask, render_template, flash, redirect, url_for
from app import app
from .forms import LoginForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from models import OAuthSignIn


@app.route('/')
@app.route('/index')
def index():
	user = {'nickname': 'Suzie'} 
	posts = [
	{
		'author': {'nickname': 'John'},
		'body': 'Beautiful day in California!'
	},
	{
		'author': {'nickname': 'Kay'},
		'body': 'Just came back from Korea'
	}
	]
	return render_template ('index.html', user=user, posts = posts)



@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login requested for OpenID="%s", remember_me=%s' %
				(form.openid.data, str(form.remember_me.data)))
		return redirect('/index')
	return render_template('login.html', title = 'Sign In', form = form, providers=app.config['OPENID_PROVIDERS'])




@app.route('/authorize/<provider>')
def oauth_authorize(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()



@app.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None:
		flash('Authentication failed')
		return redirect(url_for('index'))
	user = User.query.filter_by(social_id = social_id).first()
	if not user:
		user = User(social_id = social_id, nickname=username, email=email)
		db.session.add(user)
		db.session.commit()
	login_user(user, True)
	return redirect(url_for('index'))

