import os

MODEL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

AUDIO_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data','audio')

# Model paths

SUMMARY_BART_MODEL = os.path.join(MODEL_FOLDER, 'v1.0.0-bart')

TITLE_MODEL = os.path.join(MODEL_FOLDER, 'v1.0.0-bart-title')

JARGONS_TEXT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data','jargons.txt')

LIVE_TRANSCRIPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'views','temp','data.txt')