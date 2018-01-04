import os
<<<<<<< HEAD
GOOGLE_CLIENT_KEY = os.environ.get("GOOGLE_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_SECRET")
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG") == "True"
CLIENT_SECRETS_FILE = "client_secret.json"
=======

GOOGLE_CLIENT_KEY=os.getenv("GOOGLE_CLIENT_KEY")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY=os.getenv("SECRET_KEY")
>>>>>>> acda66ab4358048bd42954ca9ee27a91bc486425
