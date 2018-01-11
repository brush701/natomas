import os

GOOGLE_CLIENT_KEY = os.environ.get("GOOGLE_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_SECRET")
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG") == "True"
CLIENT_SECRETS_FILE = "client_secret.json"
