from util import process_voice
import os

# transcribe all mp3 files in call_logs dir to txt files
def transcribe_directory_wav_to_txt(directory_path):
    counter = 0  # Initialize counter for file naming
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.wav'):
                wav_path = os.path.join(root, file)
                try:
                    # Transcribe the wav file to text
                    transcribed_text = process_voice(wav_path)
                    # Save the transcribed text to a .txt file
                    output_filename = f'call_log{counter}.txt'
                    output_path = os.path.join(root, output_filename)
                    with open(output_path, 'w') as text_file:
                        text_file.write(transcribed_text)
                    print(f'Transcribed "{wav_path}" to "{output_path}"')
                    counter += 1
                except Exception as e:
                    print(f'Failed to transcribe "{wav_path}": {e}')

script_directory = os.path.dirname(__file__)  # Gets the directory of the current script
target_directory_path = os.path.join(script_directory, '..\call_logs')  # Adjust the path to where your MP3 files are
# Example usage
transcribe_directory_wav_to_txt(target_directory_path)