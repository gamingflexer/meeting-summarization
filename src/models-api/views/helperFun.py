from views.preprocessing import transcript_preprocesssing, email_grabber, date_grabber, get_phone_numbers, get_human_name, address_grabber, correct_sentence, get_jargon_sentences, detect_meeting_structure,detect_questions_answers, g_translation_en
from views.postprocessing import clean_summary, format_summary
from model.models import action_items_distil_bert
from spellchecker import SpellChecker
import pandas as pd
from .models import ModelSelect

from decouple import config
DEBUG = config('DEBUG', cast=bool)
if DEBUG == False:
    from views.transcript import TranscriptPreProcessor

spell = SpellChecker()

class PreProcesssor(): # which features are taken totally depends on the meeting type
    
    def __init__(self, text):
        
        self.text = transcript_preprocesssing(text)
        self.og_text = text
        
    def get_entites(self):
        text = self.text
        email = email_grabber(text) #set
        date = date_grabber(text) #list
        phone_numbers = get_phone_numbers(text) #list 
        addresses = address_grabber(text) #list
        return email,date,phone_numbers,addresses
    
    def speaker_names(self):
        human_names = get_human_name(self.text)
        return human_names
    
    def get_corrected_text(self,cleaned_text):
        corrected_text = correct_sentence(cleaned_text,spell)
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
    
    def tranlate_text(self):
        text = self.og_text
        #translate text
        text = g_translation_en(text)
        return text
    
    def get_action_items(self,corrected_text):
        #getting top list
        
        top_list = action_items_distil_bert(corrected_text)
        return top_list.keys()
    
class PostProcesssor():
    
    def __init__(self, text):
        self.text = text
        
    def get_clean_summary(self):
        clean_summaries = clean_summary(self.text)
        return clean_summaries
    
    def get_formatted_summary(self,cleaned_summary):
        formatted_summary = format_summary(cleaned_summary)
        return formatted_summary
    
def processors_call_on_trancript(transcript_df,transcript_joined): # in the format of the json | whisper
            
    # non-formatted transcript preprocessor [WORKS NON FORMATTED]
    trancript_object = PreProcesssor(transcript_joined)
    email,date,phone_numbers,addresses = trancript_object.get_entites()
    speaker_names = trancript_object.get_speaker_names()
    corrected_text = trancript_object.get_corrected_text()
    jargon_sentences = trancript_object.get_jargon_sentences(corrected_text)
    action_items_list = trancript_object.get_action_items(corrected_text)
    
    trancript_prepocessor_object = TranscriptPreProcessor(backchannels = "nlp")
    analyse_transcript_var = trancript_prepocessor_object.analyse_transcript(transcript_df)
    get_interactions_silence = trancript_prepocessor_object.get_interactions_silence(transcript_df)
    backchannels = trancript_prepocessor_object.get_backchannels(transcript_df)
    stats = trancript_prepocessor_object.get_stats(transcript_df) #speaker stats
    #df_cluster = trancript_prepocessor_object.get_cluster(df).to_json(orient='records') # what to do with this?

    return {
            "meta_data":{"email":email,
                        "imp_dates":date,
                        "phone_numbers":phone_numbers,
                        "human_names":speaker_names,
                        "addresses":addresses,
                        "jargon_sentences":jargon_sentences,
                        "action_items":action_items_list,
                        "analyse_transcript":analyse_transcript_var,
                        "get_interactions_silence":get_interactions_silence,
                        "backchannels":backchannels,
                        "stats":stats,
                        #"df_cluster":df_cluster
                        }} 