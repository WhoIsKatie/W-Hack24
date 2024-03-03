from flask import request
from openai import OpenAI
import os
import speech_recognition as sr

def feng_analysis(email_message):
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    completion = client.chat.completions.create(
    model="ft:gpt-3.5-turbo-0125:personal:uottawahack3:8yWNYh5I",
    messages=[
        {"role": "system", "content": """
        Given the input email and the reponse determine if the email provided below is safe or potentially malicious based on its
    content. If the email seems legitimate and does not contain any
    harmful intent, threats, or suspicious requests, classify it as
    "safe". If the email contains elements typical of phishing attempts,
    such as requests for sensitive information, suspicious links, or unusual
    sender addresses, classify it as "potentially malicious".
        """},
        {"role": "user", "content": 
        email_message} # Write your prompt in here
    ]
    )
    return(completion.choices[0].message)


def process_voice(voice_file):
    # Convert voice data to text
    recognizer = sr.Recognizer()
    with sr.AudioFile(voice_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(voice_file)
            print(f"Transcribed text: {text}")
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

def get_calls():
    call_logs = []
    call_logs_folder = './call_logs' 

    # Assuming call_logs is a folder containing text files
    for filename in os.listdir(call_logs_folder):
        with open(os.path.join(call_logs_folder, filename), 'r') as file:
            content = file.read()
            call_logs.append(content)

    return call_logs