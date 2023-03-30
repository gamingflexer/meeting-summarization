from views.preprocessing import transcript_preprocesssing, email_grabber, date_grabber, get_phone_numbers, get_human_name, address_grabber, correct_sentence, get_jargon_sentences, detect_meeting_structure,detect_questions_answers, g_translation_en
from views.postprocessing import clean_summary, format_summary
from model.models import action_items_distil_bert
from views.transcript import TranscriptPreProcessor
from spellchecker import SpellChecker
import pandas as pd
from model.models import ModelSelect

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
    
def processors_call_on_trancript(transcript): # in the format of the json | whisper
    transcript_joined = ""
    for segment in transcript:
        transcript_joined += segment['text'] # no speaker info
            
    # non-formatted transcript preprocessor
    trancript_object = PreProcesssor(transcript_joined)
    email,date,phone_numbers,addresses = trancript_object.get_entites()
    speaker_names = trancript_object.get_speaker_names()
    corrected_text = trancript_object.get_corrected_text()
    jargon_sentences = trancript_object.get_jargon_sentences(corrected_text)
    action_items_list = trancript_object.get_action_items(corrected_text)
    
    # formatted transcript preprocessor
    
    #Convert to DataFrame
    df = pd.DataFrame(transcript) ########## this is the transcript
    
    trancript_prepocessor_object = TranscriptPreProcessor()
    analyse_transcript_var = trancript_prepocessor_object.analyse_transcript(df)
    get_interactions_silence = trancript_prepocessor_object.get_interactions_silence(df)
    backchannels = trancript_prepocessor_object.get_backchannels(df)
    stats = trancript_prepocessor_object.get_stats(df)
    df_cluster = trancript_prepocessor_object.get_cluster(df) # what to do with this?
    
    new_model = ModelSelect(modelname = 'bart',model_id_or_path= 'knkarthick/MEETING_SUMMARY',text = transcript,max_new_tokens=200)
    model = new_model.load_model()
    summary_main = new_model.generate_summary(model)
    
    # postprocessor on the summary
    summary_main_object = PostProcesssor(summary_main)
    clean_summary = summary_main_object.get_clean_summary()
    formatted_summary = summary_main_object.get_formatted_summary(clean_summary)
    
    return {"summary": formatted_summary, 
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
                        "df_cluster":df_cluster}} 