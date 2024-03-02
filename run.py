from flask import Flask, render_template, request
from app import util

app = Flask(__name__)

# Route for receiving voice data
@app.route('/voice', methods=['POST'])
def receive_voice():
    # Process voice data (convert to text, send to ML model)
    # For example:
    voice_data = request.form['voice_data']
    # Send voice data to ML model
    processed_text = util.process_voice(voice_data)
    return processed_text

# Route for serving web page
@app.route('/')
def index():
    # Render HTML template
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
