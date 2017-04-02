from app import db, lm
from flask_login import UserMixin
from flask import current_app, url_for, request, redirect, session

from rauth import OAuth2Service



class OAuthSignIn(object):
	providers = None

	def __init__(self, provider_name):
		self.provider_name = provider_name
		credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
		self.consumer_id = credentials['id']
		self.consumer_secret = credentials['secret']

	def authorize(self):
		pass

	def callback(self):
		pass

	def get_callback_url(self):
		return url_for('oauth_callback', provider=self.provider_name, _external=True)
	
	@classmethod
	def get_provider(self, provider_name):
		if self.providers is None:
			self.providers = {}
			for provider_class in self.__subclasses__():
				provider = provider_class()
				self.providers[provider.provider_name] = provider
		return self.providers[provider_name]



class FacebookSignIn(OAuthSignIn):
	def __init__(self):
		super(FacebookSignIn, self).__init__('facebook')
		self.service = OAuth2Service(
			name = 'facebook',
			client_id = self.consumer_id,
			client_secret = self.consumer_secret,
			authorize_url='https://graph.facebook.com/oauth/authorize',
			access_token_url = 'https://graph.facebook.com/oauth/access_token',
			base_url='https://graph.facebook.com'
			)

		def authorize(self):
			return redirect(self.service.get_authorize_url(
				scope = 'email',
				response_type = 'code',
				redirect_uri = self.get_callback_url())
			)

		def callback(self):
			if 'code' not in request.args:
				return None, None, None
			oauth_session = self.service.get_auth_session(
				data = {'code': request.args['code'],
						'grant_type': 'authorization_code',
						'redirect_uri': self.get_callback_url()}
						)
			me = oauth_session.get('me?fields=id,email').json()
			return ( 
				'facebook$' + me['id'],
				me.get('email').split('@')[0],
				me.get('email)')
				)



class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64), index=True, unique=True)
	social_id = db.Column(db.String(64), nullable=False, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	posts = db.relationship('Post', backref='author', lazy='dynamic')

	def __repr__(self):
		return '<User %r>' % (self.nickname)

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.body)