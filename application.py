from flask import Flask, redirect, url_for, session, request, jsonify, g
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from oauth2client.contrib import xsrfutil
from functools import wraps
import requests
import json
import os
import pdb

application = Flask(__name__, instance_relative_config=True)
application.config.from_object('config')
application.config.from_pyfile('config.py')

@application.route('/')
def index():
  return print_index_table()

@application.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      application.config["CLIENT_SECRETS_FILE"], scopes=application.config["GOOGLE_SCOPES"])

  flow.redirect_uri = url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  session['state'] = state

  return redirect(authorization_url)


@application.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      application.config["CLIENT_SECRETS_FILE"], scopes=application.config["GOOGLE_SCOPES"], state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    info = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
        headers = {'Authorization': 'Bearer ' + flow.credentials.token})

    status_code = getattr(info, 'status_code')
    if status_code == 200:
      return(info.text)
    else:
      return('An error occurred.' + print_index_table())

@application.route('/revoke')
def revoke():
  if 'credentials' not in session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **session['credentials'])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@application.route('/clear')
def clear_credentials():
  if 'credentials' in session:
    del session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())

#verify that email is in session and that it matches an authorized user
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not valid:
            return redirect(url_for('authorize', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@application.route('/secret')
@login_required
def test_secret():
    return '<p>success</p>'

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  if application.config["DEBUG"]:
      os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  obj = {}
  obj["web"] = {}
  obj["web"]["client_id"] = application.config["GOOGLE_CLIENT_KEY"]
  obj["web"]["project_id"] = application.config["GOOGLE_PROJECT_ID"]
  obj["web"]["auth_uri"] = application.config["GOOGLE_AUTH_URI"]
  obj["web"]["token_uri"] = application.config["GOOGLE_TOKEN_URI"]
  obj["web"]["auth_provider_x509_cert_url"] = application.config["GOOGLE_AUTH_PROVIDER_X509_CERT_URL"]
  obj["web"]["client_secret"] = application.config["GOOGLE_CLIENT_SECRET"]
  obj["web"]["redirect_uris"] = application.config["GOOGLE_REDIRECT_URIS"]
  obj["web"]["javascript_origins"] = application.config["GOOGLE_JAVASCRIPT_ORIGINS"]
  with open(application.config["CLIENT_SECRETS_FILE"], 'w') as outfile:
      json.dump(obj, outfile)

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  application.run('127.0.0.1', 8080, debug=True)
