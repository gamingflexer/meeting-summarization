import whisper
import spacy

from transformers import pipeline
from transformers import TFAutoModelForSeq2SeqLM,PegasusForConditionalGeneration

from model.models import bart_summarize,longformer_summarize,pegasus_summarize
from preprocessing import transcript_preprocesssing

def wav_to_transcript(wav_file_path,model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(wav_file_path)
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
        else:
            print("\nModel not found\n")
            
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
            summary = longformer_summarize(model, self.text, self.max_new_tokens)
            return summary
        elif self.modelname == "pegasus":
            summary = pegasus_summarize(model, self.text)
        else:
            print("\nModel not loaded\n")
            print("\nModel not loaded\n")
        
            
# newmodel = ModelSelect("bart")
# model = newmodel.load_model()
# results = newmodel.generate_summary(model)