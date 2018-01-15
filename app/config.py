import os

SECRET_KEY_FILE = "/run/secrets/secret-key"
with open(SECRET_KEY_FILE, 'r') as file:
    SECRET_KEY = file.read()
DEBUG = os.environ.get("DEBUG") == "True"
CLIENT_SECRETS_FILE = "/run/secrets/client-secret"
GOOGLE_SCOPES = ["email", "profile"]
