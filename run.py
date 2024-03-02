from flask import Flask, session, request, redirect, render_template
import google_auth_oauthlib.flow
from app import util
import secrets, os
import requests

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/gmail.readonly'])
flow.redirect_uri = 'https://127.0.0.1:5000/oauth2callback'


@app.route('/')
def start():
    # Redirect to Google authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent')
    return redirect(authorization_url)

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

    url = f'https://gmail.googleapis.com/gmail/v1/users/{userId}/messages'
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json()
        # Process the retrieved messages
    else:
        print(f'Error: {response.status_code} - {response.text}')
    return redirect('/index')

@app.route('/index')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, ssl_context=('server.crt', 'server.key'))
