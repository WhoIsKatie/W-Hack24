from flask import Flask, session, request, redirect, render_template
import google_auth_oauthlib.flow
from app import util
import secrets, os

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
    # authorization_response = request.url
    # flow.fetch_token(authorization_response=authorization_response)
    # session['credentials'] = flow.credentials
    return redirect('/index')

@app.route('/index')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, ssl_context=('server.crt', 'server.key'))
