from flask import Flask, redirect, url_for, session, request, jsonify
from authlib.client.apps import google
from authlib.flask.client import OAuth
import json
import os

application = Flask(__name__, instance_relative_config=True)
application.config.from_object('config')
application.config.from_pyfile('config.py')
application.secret_key = application.config["SECRET_KEY"]

oauth = OAuth(application)
google.register_to(oauth)

@application.route('/')
def index():
    if 'google_token' in session:
        token = session["google_token"]
        user = google.parse_openid(token)
        return json.dumps(user)
    return redirect(url_for('login'))


@application.route('/login')
def login():
    callback_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(callback_uri)


@application.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


@application.route('/oauth2callback')
def authorized():
    try:
        token = google.authorize_access_token()
    except OAuthException as e:
        return "Access denied: {}".format(e)
    session['google_token'] = token
    user = google.parse_openid(token)
    return json.dumps(user)

if __name__ == '__main__':
    application.run()
