import gdown

ALLOWED_EXTENSIONS = (['wav','csv','mp3','.acc'])

def drive_download(url, output):
    gdown.download(url, output, quiet=False)
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import wordnet

def sentiment_check(text):
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