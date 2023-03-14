import re
import nltk
import spacy
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from date_extractor import extract_dates
from deep_translator import GoogleTranslator

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

# load the English language model
nlp = spacy.load("en_core_web_sm")

def transcript_preprocesssing(text):
    text = "".join(text.split('\n'))  # remove whitespaces
    text = text.lower()

    # using re
    text = re.sub('http\S+\s*', ' ', text)
    text = re.sub('RT|cc', ' ', text)
    text = re.sub('#\S+', ' ', text)
    #text = re.sub('@\S+', ' ', text)


    text = re.sub(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', '', text)  # removes phone numbers
    text = re.sub(r'[^\x00-\x7f]', ' ', text)
    text = re.sub('\s+', ' ', text)
    text = re.sub("\n", " ", text)
    text = text.replace("]", "'")
    text = text.replace("[", "'")
    
    return text

def email_grabber(text):
    try:
      emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
      emails=set(emails)
    except:
      emails = "None"
    return(emails)

def get_phone_numbers(string):
    r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    phone_numbers = r.findall(string)
    return [re.sub(r'\D', '', num) for num in phone_numbers]

# dates grabber
def date_grabber(text):
    dates = extract_dates(text)
    return dates

def get_human_name(text):
    person_list = []
    nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
    for nltk_result in nltk_results:
        if type(nltk_result) == Tree:
            name = ''
            for nltk_result_leaf in nltk_result.leaves():
                name += nltk_result_leaf[0] + ' '
            person_list.append(name.strip())
    return person_list

def address_grabber(text):
    regexp = "[0-9]{1,3} .+, .+, [A-Z]{2} [0-9]{5}"
    address = re.findall(regexp, text)
    #addresses = pyap.parse(text, country='INDIA')
    return address

def correct_sentence(sentence,spell):
    # Split sentence into words
    words = sentence.split()
    # Correct misspelled words
    incorrect_words = []
    corrected_words = []
    for word in words:
        # Check if the word is misspelled
        if spell.unknown([word]):
            # Get the corrected version of the word
            corrected_word = spell.correction(word)
            corrected_words.append(corrected_word)
            incorrect_words.append(corrected_word)
        else:
            corrected_words.append(word)
    # Join corrected words back into sentence
    #corrected_sentence = ' '.join(corrected_words)
    return corrected_words

def get_jargon_sentences(transcript):
    
    doc = nlp(transcript)

    jargon_list = ["AI", "machine learning", "neural network", "big data", "algorithm"]
    
    with open("src/models-api/data/jargons.txt", "r") as f:
        jargon_list.append(f.read().splitlines())
    
    jargon_sentences = []
    jargons = []
    for sent in doc.sents:
        # check if any jargon words appear in the sentence
        if any(token.text in jargon_list for token in sent):
            jargon_sentences.append(sent.text)
            jargons.append([token.text for token in sent if token.text in jargon_list])
            
    return jargon_sentences

def detect_meeting_structure(transcript):
    sections = []
    
    # Look for keywords indicating the start of different sections
    agenda_start = re.search(r'Agenda:', transcript, re.IGNORECASE)
    discussion_start = re.search(r'Discussion:', transcript, re.IGNORECASE)
    action_items_start = re.search(r'Action Items:', transcript, re.IGNORECASE)
    decision_start = re.search(r'Decisions:', transcript, re.IGNORECASE)
    conclusion_start = re.search(r'Conclusion:', transcript, re.IGNORECASE)
    
    # If a section start is found, add the section to the list of sections
    if agenda_start:
        sections.append(transcript[agenda_start.end():])
    if discussion_start:
        sections.append(transcript[discussion_start.end():])
    if action_items_start:
        sections.append(transcript[action_items_start.end():])
    if decision_start:
        sections.append(transcript[decision_start.end():])
    if conclusion_start:
        sections.append(transcript[conclusion_start.end():])
    
    return sections

def detect_questions_answers(transcript):
    questions = []
    answers = []

    # Process the transcript using spaCy
    doc = nlp(transcript)

    # Loop through each sentence in the transcript
    for sent in doc.sents:
        # Check if the sentence is a question
        if sent[-1].text == '?':
            # Add the sentence to the list of questions
            questions.append(sent.text)
        # Check if the sentence is an answer to a previous question
        elif sent[0].text.lower() == 'yes' or sent[0].text.lower() == 'no':
            answers.append(sent.text)

    return questions, answers

def g_translation_en(inText):
  try:
    if len(inText)<=4999:
      outText = GoogleTranslator(target='en').translate(inText)
      return outText
    else:
      return ""
  except Exception as e:
    print(e)
    pass

"""
GET CLUSTTERS IN THE TRANSCRIPT | NOT USED
"""

def return_q_a_others(sentences, max_check=True):
    
    if max_check:
        max_check_num = 5 
    else:
        max_check_num = len(sentences)
        
    num_questions = 0
    num_answers = 0
    
    question_verbs = ['ask', 'answer', 'question', 'answer', 'tell', 'explain', 'describe', 'define', 'clarify', 'elaborate', 'demonstrate', 'illustrate', 'show', 'state', 'mention', 'discuss','What','how','I have a','Is there', 'One more', 'Can we']
    
    # Loop through each sentence and count the number of questions and answers
    for sent in sentences[:max_check_num]:
        doc = nlp(sent)
        
        # Check if the sentence is a question
        if doc[-1].text == '?':
            num_questions += 1

        else:
            for verb in question_verbs:
                if verb in sent:
                    num_questions += 1
                else:
                    num_answers += 1
        
    
    # Check which type of sentence occurs more frequently
    if num_questions > num_answers:
        return "questions"
    elif num_answers > num_questions:
        return "answers"
    elif len(doc) > 6:
        return "others"
    else:
        return "mixed_type"

def transcript_clusterer(transcript_text, n_clusters=4):
    # Load the English language model in spacy
    nlp = spacy.load("en_core_web_sm")

    # Split the transcript into individual sentences
    doc = nlp(transcript_text)
    sentences = [str(sent).strip() for sent in doc.sents]

    # Create a feature matrix using spacy's vector representation of each sentence
    X = np.array([sent.vector for sent in doc.sents])

    # Determine the optimal number of clusters using the elbow method
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
        kmeans.fit(X)
        wcss.append(kmeans.inertia_)

    # Fit the k-means clustering model to the data
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=300, n_init=10, random_state=0)
    y_kmeans = kmeans.fit_predict(X)

    # Add cluster labels to each sentence
    df = pd.DataFrame({'sentences': sentences, 'cluster': y_kmeans})

    # Group the sentences by cluster label and return a dictionary
    clusters = {}
    for i in range(n_clusters):
        clusters[f'Cluster {i}'] = {"sentences" :(df.loc[df['cluster'] == i, 'sentences'])}
    
    return clusters

#main Function
def get_clusters(transcript):
    cls = transcript_clusterer(transcript)
    for k, v in cls.items():
        if len(v['sentences']) > 6:
            for sentence in v['sentences']:
                sentiment = return_q_a_others(sentence)
            cls[k]['label'] = sentiment
        else:
            cls[k]['label'] = "others"
            
    return cls