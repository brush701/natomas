from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

application = Flask(__name__)
application.config['GOOGLE_ID'] = os.environ.get("GOOGLE_ID")
application.config['GOOGLE_SECRET'] = os.environ.get("GOOGLE_SECRET")
application.debug = True
application.secret_key = 'development'
oauth = OAuth(application)

google = oauth.remote_app(
    'google',
    consumer_key=application.config.get('GOOGLE_ID'),
    consumer_secret=application.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


@application.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        return jsonify({"data": me.data})
    return redirect(url_for('login'))


@application.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@application.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


@application.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    return jsonify({"data": me.data})


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


if __name__ == '__main__':
    application.run()
