import whisper
import spacy

from transformers import pipeline
from transformers import TFAutoModelForSeq2SeqLM,PegasusForConditionalGeneration,AutoModel,AutoTokenizer,AutoModelForSeq2SeqLM

from model.models import bart_summarize, longformer_summarize, pegasus_summarize, bart_title_summarizer
from model.extractive import extract_sentences
from model.retrieval import chatbot_response
from views.preprocessing import transcript_preprocesssing

import noisereduce as nr
import librosa as rosa
import soundfile as sf
import random as rd
import whisper
from datetime import timedelta
import os

from config import AUDIO_FOLDER

def audio_enhance(file):
    audio_data, sample_rate = rosa.load(file, sr=16000)
    reduced_noise = nr.reduce_noise(y = audio_data, sr=sample_rate, n_std_thresh_stationary=1.5,stationary=True)
    path_to_save = os.path.join(AUDIO_FOLDER,f"file_{rd.random(0.1)}.wav")
    sf.write(path_to_save,reduced_noise,sample_rate, 'PCM_24')
    return path_to_save 

def wav_to_transcript(wav_file_path,model_name="base", segments = False):
    model = whisper.load_model(model_name)
    result = model.transcribe(wav_file_path)
    if segments:
        return result['segments']
    return result

def transcript_to_summary(transcript):
    transcript = transcript_preprocesssing(transcript)
    return transcript

def transcript_to_entities(transcript):
    transcript = transcript_preprocesssing(transcript)
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(transcript)
    return doc.ents

class ModelSelect():
    
    def __init__(self,modelname,text,max_new_tokens):
        self.modelname = modelname
        #self.model_id_or_path = self.model_id_or_path
        self.text = text
        self.max_new_tokens = max_new_tokens
        
    def load_model(self,model_id_or_path):
        if self.modelname == "bart":
            model = pipeline("summarization", model=model_id_or_path)
            return model
        elif self.modelname == "longformer":
            model = TFAutoModelForSeq2SeqLM.from_pretrained(model_id_or_path,from_pt=True)
            return model
        elif self.modelname == "pegasus":
            model = PegasusForConditionalGeneration.from_pretrained(model_id_or_path)
        elif self.modename == "title":
            model = AutoModelForSeq2SeqLM.from_pretrained(model_id_or_path)
        else:
            print("\nModel not found\n")
        return model
            
    def de_load_all_model(self):
        del model
        
        from numba import cuda
        import torch
        
        if torch.cuda.is_available():
            device = cuda.get_current_device()
            device.reset()
            
    def generate_summary(self,model,model_path_local):
        if self.modelname == "bart":
            summary = bart_summarize(model,self.text)
            return summary
        elif self.modelname == "longformer":
            summary = longformer_summarize(model, self.text, self.max_new_tokens)
            return summary
        elif self.modelname == "pegasus":
            summary = pegasus_summarize(model, self.text)
        elif self.modename == "title":
            summary = bart_title_summarizer(model,model_path_local,self.text)
            return summary
        else:
            print("\nModel not loaded\n")
            
    def nlp_extractive_summary(self, list_output = False):
        #Basic NLP extractive summary
        extract_sentence,questions_and_answers = extract_sentences(self.text) #list of sentences
        joined_sentences = " ".join(extract_sentence)
        if list_output:
            return extract_sentence
        return joined_sentences
    
    def extractive_summary(self):
        #Extractive summary
        return self.text
    
            
# newmodel = ModelSelect("bart")
# model = newmodel.load_model()
# results = newmodel.generate_summary(model)

class ChatBot():
    def __init__(self,question,transcript,summary,model_name="sentence-transformers/paraphrase-MiniLM-L6-v2"):
        self.question = question
        self.transcript = transcript
        self.summary = summary
        self.model_name = model_name
        
    def load_chatbot(self):
        model = AutoModel.from_pretrained(self.model_name)
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        return model,tokenizer
        
    def chatbot_answer(self,tokenizer,model):
        return chatbot_response(self.question,self.transcript,self.summary,tokenizer,model)