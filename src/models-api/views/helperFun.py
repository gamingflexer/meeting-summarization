from preprocessing import transcript_preprocesssing, email_grabber, date_grabber, get_phone_numbers, get_human_name, address_grabber, correct_sentence, get_jargon_sentences, detect_meeting_structure,detect_questions_answers
from postprocessing import clean_summary, format_summary
from spellchecker import SpellChecker

spell = SpellChecker()

class pre_processsor():
    
    def __init__(self, text):
        self.text = transcript_preprocesssing(text)
        
    def get_entites(self):
        text = self.text
        email = email_grabber(text) #set
        date = date_grabber(text) #list
        phone_numbers = get_phone_numbers(text) #list
        human_name = get_human_name(text) #list
        addresses = address_grabber(text) #list
        return email,date,phone_numbers,human_name,addresses
    
    def get_corrected_text(self):
        text = self.text
        corrected_text = correct_sentence(text,spell)
        return corrected_text
    
    def get_jargon_sentences(self):
        text = self.text
        jargon_sentences = get_jargon_sentences(text)
        return jargon_sentences
    
    def get_meeting_structure(self):
        text = self.text
        meeting_structure = detect_meeting_structure(text)
        question,answers = detect_questions_answers(text)
        return meeting_structure,[question,answers]
    
class post_processsor():
    
    def __init__(self, text):
        self.text = text
        
    def get_clean_summary(self):
        clean_summaries = clean_summary(self.text)
        return clean_summaries
    
    def get_formatted_summary(self):
        formatted_summary = format_summary(self.text)
        return formatted_summary