import re
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from date_extractor import extract_dates

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


def email(text):
    try:
      #text = pre_process1_rsw1(text)
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
