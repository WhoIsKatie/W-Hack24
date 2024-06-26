import time

from flask import Flask, request, redirect, render_template, jsonify

import google_auth_oauthlib.flow
from app import util
import secrets
import requests
from base64 import urlsafe_b64decode
import json

import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from joblib import load

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

TOKEN_FILE = 'access_token.json'
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/gmail.readonly'])
flow.redirect_uri = 'https://127.0.0.1:5000/oauth2callback'

sender_array, subject_array, date_array, body_array = [], [], [], []

# load the model
model_path = os.path.join('model', 'email_classifier_model.joblib')
model = load(model_path)

## example use
# incoming_text_data = "whatever"
# predictions = model.predict([incoming_text_data])
# print(predictions[0])
# probabilities = model.predict_proba([incoming_text_data])
# print(f"Confidence: {max(probabilities[0])*100:.2f}%")
## the return value is an array, so you need to access the first index

@app.route('/')
def start():
    if os.path.exists(TOKEN_FILE):
        # Token exists, redirect to index directly
        return redirect('/index')
    else:
    # Redirect to Google authorization URL
        authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent')
        return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    userId = 'me'

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            access_token = token_data.get('access_token')
    else:
        # Get the authorization code from the callback URL
        authorization_response = request.url
        # Exchange the authorization code for an access token
        flow.fetch_token(authorization_response=authorization_response)
        # Access token is now available in flow.credentials
        access_token = flow.credentials.token

        # Save the token to a file
        with open(TOKEN_FILE, 'w') as f:
            json.dump({'access_token': access_token}, f)
    
    get_emails()

    return redirect('/index')

@app.route('/index')
def index():
    get_emails()
    email_list = zip(sender_array, subject_array, date_array)
    return render_template('index.html', email_list=email_list, body_array=body_array)

@app.route('/calls', methods=['GET'])
def calls():
    logs = util.get_calls()
    return render_template('call_tab.html', call_list=logs, body_array=logs)

# Route for receiving voice data
@app.route('/voice', methods=['POST'])
def receive_voice():
    # Process voice data (convert to text, send to ML model)
    # For example:
    voice_data = request.form['voice_data']
    # Send voice data to ML model
    processed_text = util.process_voice(voice_data)
    return processed_text

# helper to preprocess text
def preprocess_text(text):
    # Cleaning: remove special characters and extra spaces
    # text = re.sub(r'[\t\n\r]+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s.,;\'\":-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenization
    tokens = nltk.word_tokenize(text)

    # Stop Words Removal
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.lower() not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]

    # Rejoin tokens into a single string
    return ' '.join(tokens)

@app.route('/ping', methods=['POST'])
def ping():
    body = request.data
    incoming_text_data = body.decode('utf-8')
    richard_predictions = model.predict([preprocess_text(incoming_text_data)])
    feng_predictions = util.feng_analysis(incoming_text_data)
    # classification
    print(richard_predictions[0], feng_predictions)
    richard_probabilities = model.predict_proba([incoming_text_data])
    print(f"Confidence: {max(richard_probabilities[0])*100:.2f}%")
    if((feng_predictions == "Safe" and richard_predictions[0] != "Malicious Email") or (feng_predictions == "Potentially Malicious" and richard_predictions[0] == "Malicious Email")):
        return jsonify({"message": feng_predictions.content, "confidence": f"{max(richard_probabilities[0])*100:.2f}%", "opposite": richard_predictions[0], "opposite_confidence": f"{max(richard_probabilities[0])*100:.2f}%"})

    if((feng_predictions == "Potentially Malicious" and richard_predictions[0] != "Malicious Email") or (feng_predictions == "Safe" and richard_predictions[0] == "Malicious Email")):
        return jsonify({"message": "Potentially Malicious", "opposite": "Had conflicting views - take caution!", "opposite_confidence": "N/A"})
    
    return jsonify({"message": richard_predictions[0], "opposite": feng_predictions.content, "opposite_confidence": "N/A"})

def get_emails():
    # If the arrays are already populated, don't do anything
    if sender_array and subject_array and date_array and body_array:
        return

    userId = 'me'
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)
        access_token = token_data.get('access_token')

    headers = {'Authorization': f'Bearer {access_token}'}
    all_messages_url = f'https://gmail.googleapis.com/gmail/v1/users/{userId}/messages'
    response = requests.get(all_messages_url, headers=headers, params={'q': "is:inbox -from:me"})

    if response.status_code != 200:
        print(f'Error: {response.status_code} - {response.text}')


    for message in response.json()['messages'][0:10]:
        message_id = message['id']
        message_url = f'https://gmail.googleapis.com/gmail/v1/users/{userId}/messages/{message_id}'
        message_response = requests.get(message_url, headers=headers)
        if message_response.status_code == 200:
            message_data = message_response.json()
            header_data = message_data['payload']['headers'] #it's an array of dictionaries which have 'name' and 'value'
            body_data = message_data['payload']['body']['data'] if 'data' in message_data['payload']['body'] else message_data['payload']['parts'][0]['body']['data']
            body_data = urlsafe_b64decode(body_data).decode('utf-8')
            body_array.append(body_data)

            for header in header_data:
                if header['name'] == 'From':
                    sender_array.append(header['value'])
                elif header['name'] == 'Subject':
                    subject_array.append(header['value'])
                elif header['name'] == 'Date':
                    date_array.append(header['value'])

if __name__ == '__main__':
    app.run(debug=True, ssl_context=('server.crt', 'server.key'))