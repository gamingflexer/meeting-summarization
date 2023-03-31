import re
import os
import nltk
import time
import spacy
import gdown
import logging
from decouple import config
from config import AUDIO_FOLDER 
from nltk.corpus import wordnet
from nltk.sentiment import SentimentIntensityAnalyzer
from moviepy.video.io.VideoFileClip import VideoFileClip

DEBUG = config('DEBUG', cast=bool)

if not DEBUG:
    import nltk
    nltk.download('wordnet')
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('vader_lexicon')
    nltk.download('averaged_perceptron_tagger')
    nlp = spacy.load('en_core_web_lg')
else:
    nlp = spacy.load('en_core_web_sm')

ALLOWED_EXTENSIONS = [
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v', '.webm', '.mpeg',
    '.mp3', '.wav', '.m4a', '.aac', '.ogg', '.wma', '.flac', '.alac', '.opus'
] 

def format_server_time():
  server_time = time.localtime()
  return time.strftime("%I:%M:%S %p", server_time)

def drive_download(url, output):
    gdown.download(url, output, quiet=False)
    
def allowed_file(filename):
    _, file_extension = os.path.splitext(filename)
    return file_extension.lower() in ALLOWED_EXTENSIONS

def sentiment_reverser(text):
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(text)['compound']
    if sentiment_score < 0:
        # if sentiment is negative, remove negative words or phrases
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        new_sentence = []
        for word, tag in tagged:
            if wordnet.synsets(word) and (tag.startswith('NN') or tag.startswith('JJ') or tag.startswith('VB')):
                # keep only nouns, adjectives, and verbs
                new_word = word
                if sia.polarity_scores(word)['neg'] > 0:
                    # if word is negative, replace with antonym
                    synsets = wordnet.synsets(word)
                    for synset in synsets:
                        for lemma in synset.lemmas():
                            if lemma.antonyms():
                                new_word = lemma.antonyms()[0].name()
                                break
                new_sentence.append(new_word)
        new_text = ' '.join(new_sentence[1:])
        return new_text
    else:
        # if sentiment is positive or neutral, return original text
        return text
    
def transcript_cleaner(file_path):
    with open(file_path, 'r') as f:
        text = f.read()
    return text

def extract_audio_from_any_file(file_path):
    # Check if file is a video
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    _, file_extension = os.path.splitext(file_path)
    if file_extension not in video_extensions:
        return file_path

    # Create output directory if it does not exist
    output_dir = os.path.join(AUDIO_FOLDER, 'audio')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load video file and extract audio
    video = VideoFileClip(file_path)
    audio = video.audio

    # Generate output file path and save audio
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + '.mp3')
    audio.write_audiofile(output_file)

    return output_file


def set_global_logging_level(level=logging.ERROR, prefices=[""]):
    """
    Override logging levels of different modules based on their name as a prefix.
    It needs to be invoked after the modules have been loaded so that their loggers have been initialized.

    Args:
        - level: desired level. e.g. logging.INFO. Optional. Default is logging.ERROR
        - prefices: list of one or more str prefices to match (e.g. ["transformers", "torch"]). Optional.
          Default is `[""]` to match all active loggers.
          The match is a case-sensitive `module_name.startswith(prefix)`
    """
    prefix_re = re.compile(fr'^(?:{ "|".join(prefices) })')
    for name in logging.root.manager.loggerDict:
        if re.match(prefix_re, name):
            logging.getLogger(name).setLevel(level)