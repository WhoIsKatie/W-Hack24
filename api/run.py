import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from os import environ as env
from flask import Flask, redirect, render_template, session, url_for, request
import google_auth_oauthlib.flow
import secrets
import requests
from app import util

import api.server as server

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/gmail.readonly'])
flow.redirect_uri = 'https://127.0.0.1:5000/oauth2callback'

email_list = []


@app.route('/')
def start():
    # Redirect to Google authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent')
    return redirect(authorization_url)

# Controllers API

# Route for receiving voice data
@app.route('/voice', methods=['POST'])
def receive_voice():
    # Process voice data (convert to text, send to ML model)
    # For example:
    voice_data = request.form['voice_data']
    # Send voice data to ML model
    processed_text = util.process_voice(voice_data)
    return processed_text

@app.route('/oauth2callback')
def oauth2callback():
    userId = 'me'
    # Get the authorization code from the callback URL
    authorization_response = request.url
    # Exchange the authorization code for an access token
    flow.fetch_token(authorization_response=authorization_response)
    # Access token is now available in flow.credentials
    access_token = flow.credentials.token
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # TODO: not sure if we want to keep the stuff
    # with open('access_token.json', 'w') as f:
    #     json.dump({'access_token': access_token, 'headers': headers}, f)

    all_messages_url = f'https://gmail.googleapis.com/gmail/v1/users/{userId}/messages'
    response = requests.get(all_messages_url, headers=headers)
    
    if response.status_code != 200:
        print(f'Error: {response.status_code} - {response.text}')
    
    for message in response.json()['messages']:
        message_id = message['id']
        message_url = f'https://gmail.googleapis.com/gmail/v1/users/{userId}/messages/{message_id}'
        message_response = requests.get(message_url, headers=headers)
        if message_response.status_code == 200:
            message_data = message_response.json()
            email_list.append(message_data['payload']['headers'])
    return redirect('/index')


# Route for serving web page
@app.route('/')
def index():
    # Render HTML template
    return render_template("index.html", email_list=email_list, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
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

if __name__ == '__main__':
    server.startUp();
    app.run(debug=True, ssl_context=('server.crt', 'server.key'), port=env.get("PORT", 8000))

