import json
import logging
from datetime import datetime
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for
from functools import wraps

# B. Load .env
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# C. Initialize Flask
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# D. Configure Authlib
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# Auth decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            # Logging unauthorized access
            app.logger.warning(f"UNAUTHORIZED: Access attempt to protected route, timestamp={datetime.now()}")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    userinfo = token.get("userinfo")
    session["user"] = userinfo

    # Logging successful login
    app.logger.info(f"LOGIN: user_id={userinfo.get('sub')}, email={userinfo.get('email')}, timestamp={datetime.now()}")

    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/protected")
@requires_auth
def protected():
    user = session.get("user")

    # Logging access to protected route
    app.logger.info(f"ACCESS: /protected by user_id={user.get('sub')}, email={user.get('email')}, timestamp={datetime.now()}")

    return render_template('protected.html', user=user)


@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    #  Optional but useful: Stream logs to stdout for Azure
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=int(env.get("PORT", 3000)))
