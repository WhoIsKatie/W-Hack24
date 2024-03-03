from flask import request

from run import app
import os

def ml_analysis(text_data):
    pass
    # Placeholder code for processing voice data to text
    # text = convert_to_text(voice_data)
    # Send text to ML model for processing
    # processed_text = ml_model.process(text)
    # return processed_text
    
    # just assuming this returns array, [0] for the classification, [1] for the confidence

def process_voice(voice_data):
    pass
    # placeholder
    # assume this returns text data from voice files

def get_calls():
    call_logs = []
    call_logs_folder = './call_logs' 

    # Assuming call_logs is a folder containing text files
    for filename in os.listdir(call_logs_folder):
        with open(os.path.join(call_logs_folder, filename), 'r') as file:
            content = file.read()
            call_logs.append(content)

    return call_logs