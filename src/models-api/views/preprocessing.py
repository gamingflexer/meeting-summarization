import re
import nltk
import spacy
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from date_extractor import extract_dates

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