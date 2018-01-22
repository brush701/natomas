from flask import Flask, redirect, url_for, session, request, jsonify, g
import google_auth_oauthlib.flow
from functools import wraps
import psycopg2
import requests
import json
import os
import pdb

application = Flask(__name__)
#application.config.from_object('config')
application.config.from_pyfile('config.py')

routes = {
        "authorize": authorize,
        "oauth2callback": oauth2callback
}

# Connect to database
creds = Credentials(ServerConfig.ENVIRONMENT())
dsn = "host=%s dbname=%s user=%s password=%s" % creds.database()
connection = psycopg2.connect(dsn)
cursor = connection.cursor()

#verify that email is in session and that it matches an authorized user
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for('authorize', next=request.url))

        #TODO: check if user is authorized
        #request.headers
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', defaults={'path': ''})
@app.route("/<string:path>")
@app.route('/<path:path>')
def base(path):
    if not path:
        return print_index_table()
    else:
        global connection
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT 1')
        except:
            connection = psycopg2.connect(dsn)
            cursor = connection.cursor()

        handler = routes.get("path")
        if handler:
            data = request.get_json()
            if data:
                resp = handler(data, cursor)
                connection.commit()
        cursor.close()
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
      resp = json.loads(info.text)
      session["user"] = resp["email"]
      #TODO: lookup user in db and store role in session
      return redirect(url_for('home'))
    else:
      return('An error occurred.' + print_index_table())

@application.route('/user/home')
@login_required
def home():
    return "Hello, " + session["user"]

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '</td></tr></table>')

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  if application.config["DEBUG"]:
      os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  application.run('0.0.0.0', 8000, debug=True)
