import spacy

from transformers import pipeline,GenerationConfig
from transformers import TFAutoModelForSeq2SeqLM,PegasusForConditionalGeneration,AutoModel,AutoTokenizer,AutoModelForSeq2SeqLM,LongT5ForConditionalGeneration,LEDForConditionalGeneration

from model.models import bart_summarize, longformer_summarize, pegasus_summarize, bart_title_summarizer, longt5_summarizer, led_summarizer
# from model.extractive import extract_sentences
from views.preprocessing import transcript_preprocesssing

import noisereduce as nr
import librosa as rosa
import soundfile as sf
import random as rd
from datetime import timedelta
import os
import uuid

import tensorflow as tf
from decouple import config
DEBUG = config('DEBUG', cast=bool)
if DEBUG == False:
    gpus = tf.config.experimental.list_physical_devices('GPU')
    tf.config.experimental.set_memory_growth(gpus[0], True)
    
    import torch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    whisper2 = pipeline('automatic-speech-recognition', model = 'asach/whisper_ami_finetuned-added',chunk_length_s=30) #'/home/student/Documents/dp/v1.1/whisper_ami
    print("\nModel Loaded WHISPER \n")

from config import AUDIO_FOLDER

def audio_enhance(file): #NOT TO USED IF YOU USING FINETUNED MODEL
    audio_data, sample_rate = rosa.load(file, sr=16000)
    reduced_noise = nr.reduce_noise(y = audio_data, sr=sample_rate, n_std_thresh_stationary=1.5,stationary=True)
    path_to_save = os.path.join(AUDIO_FOLDER,f"file_{str(uuid.uuid4())}.wav")
    sf.write(path_to_save,reduced_noise,sample_rate, 'PCM_24')
    return path_to_save 

def wav_to_transcript(wav_file_path,model_name="base", segments = False):
    whisper2.model.generation_config = GenerationConfig.from_pretrained("openai/whisper-medium")
    result = whisper2(wav_file_path, return_timestamps=True)['text']
    if segments:
        for segment in result['segments']:
            segment.pop('tokens')
            segment.pop('temperature')
            segment.pop('avg_logprob')
            segment.pop('compression_ratio')
            segment.pop('no_speech_prob')
        return result['segments']
    return result

def transcript_to_summary(transcript):
    transcript = transcript_preprocesssing(transcript)
    return transcript

def transcript_to_entities(transcript):
    transcript = transcript_preprocesssing(transcript)
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(transcript)
    return doc.ents

class ModelSelect():
    
    def __init__(self,modelname,model_id_or_path,text,max_new_tokens):
        self.modelname = modelname
        self.model_id_or_path = model_id_or_path
        self.text = text
        self.max_new_tokens = max_new_tokens
        
    def load_model(self):
        if self.modelname == "bart":
            model = pipeline("summarization", model=self.model_id_or_path)
            return model
        elif self.modelname == "longformer":
            with tf.device("/gpu:0"):
                model = TFAutoModelForSeq2SeqLM.from_pretrained(self.model_id_or_path,from_pt=True)
            return model
        elif self.modelname == "pegasus":
            model = PegasusForConditionalGeneration.from_pretrained(self.model_id_or_path).to("cuda")
        elif self.modelname == "title":
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_id_or_path).to("cuda")
        elif self.modelname == "longt5":
            model = LongT5ForConditionalGeneration.from_pretrained(self.model_id_or_path).to("cuda").half()
        elif self.modelname == "led":
            model = LEDForConditionalGeneration.from_pretrained("asach/led-dialogSum-1epoch").to("cuda").half()
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
            
    def generate_summary(self,model):
        if self.modelname == "bart":
            summary = bart_summarize(model,self.text)
            return summary
        elif self.modelname == "longformer":
            summary = longformer_summarize(model,self.model_id_or_path, self.text, self.max_new_tokens)
            return summary
        elif self.modelname == "pegasus":
            summary = pegasus_summarize(model,self.model_id_or_path, self.text)
        elif self.modelname == "title":
            summary = bart_title_summarizer(model,self.model_id_or_path,self.text)
            return summary
        elif self.modelname == "longt5":
            summary = longt5_summarizer(model,self.model_id_or_path,self.text)
            return summary
        elif self.modelname == "led":
            summary = led_summarizer(model,self.model_id_or_path,self.text)
            return summary
        else:
            print("\nModel not loaded\n")
                        
    # def nlp_extractive_summary(self, list_output = False):
    #     #Basic NLP extractive summary
    #     extract_sentence,questions_and_answers = extract_sentences(self.text) #list of sentences
    #     joined_sentences = " ".join(extract_sentence)
    #     if list_output:
    #         return extract_sentence
    #     return joined_sentences
    
    # def extractive_summary(self):
    #     #Extractive summary
    #     return self.text
    
            
# newmodel = ModelSelect("bart")
# model = newmodel.load_model()
# results = newmodel.generate_summary(model)
