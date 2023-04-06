from transformers import AutoTokenizer, DistilBertForSequenceClassification, DistilBertTokenizer
import torch
import requests
import os
from config import MODEL_FOLDER

import tensorflow as tf
from decouple import config

DEBUG = config('DEBUG', cast=bool)
if DEBUG == False:
  gpus = tf.config.experimental.list_physical_devices('GPU')
  tf.config.experimental.set_memory_growth(gpus[0], True)

  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  model_state_dict = torch.load(os.path.join(MODEL_FOLDER,"bert-action-items","model.pth"),map_location = device)
  tokenizer_action = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
  # Create model instance
  model_action = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2).to("cuda")
  # Load state dictionary into model
  model_action.load_state_dict(model_state_dict)

import logging
logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)

from decouple import config
HUGGING_FACE_KEY = config('HUGGING_FACE_KEY')
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def bart_summarize(summarizer,text):
    #summarizer = pipeline("summarization", model=hub_model_id)
    summary = summarizer(text)
    return summary[0]['summary_text']

def longformer_summarize(model,model_id_or_path,text,max_new_tokens=200):
    try:
      tokenizer = AutoTokenizer.from_pretrained(model_id_or_path)
    except OSError:
      tokenizer = AutoTokenizer.from_pretrained("allenai/led-base-16384")
    #model = TFAutoModelForSeq2SeqLM.from_pretrained(hub_model_id,from_pt=True)
    try:
      text_final = "summarize: " + text
      with tf.device("/gpu:0"):
        inputs = tokenizer(text_final, return_tensors="tf").input_ids
      outputs = model.generate(inputs, max_new_tokens=max_new_tokens, do_sample=False)
      return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except IndexError:
      print(f"\n ERROR: Model not compatible with the tokeinizer or no tokenizer exits at huggingface {model_id_or_path}")
      return ""

def pegasus_summarize(model,model_id_or_path,text):
    try:
      tokenizer = AutoTokenizer.from_pretrained(model_id_or_path)
    except OSError:
      tokenizer = AutoTokenizer.from_pretrained("google/pegasus-xsum")
    #model = PegasusForConditionalGeneration.from_pretrained("")
    try:
      inputs = tokenizer(text, max_length=1024, return_tensors="pt")
      input_ids = inputs["input_ids"].to("cuda")
      summary_ids = model.generate(input_ids)
      return tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    except IndexError:
      print(f"\n ERROR: Model not compatible with the tokeinizer or no tokenizer exits at huggingface {model_id_or_path}")
      return ""

def bart_title_summarizer(model,model_path,text):
    try:
      tokenizer = AutoTokenizer.from_pretrained(model_path)
    except OSError:
      tokenizer = AutoTokenizer.from_pretrained("asach/bart-highlights-redit-new")
    encoder_max_length = 256  # demo
    decoder_max_length = 64
    inputs = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=encoder_max_length,
        return_tensors="pt",
    )
    input_ids = inputs.input_ids.to(model.device)
    attention_mask = inputs.attention_mask.to(model.device)
    outputs = model.generate(input_ids, attention_mask=attention_mask)
    outputs_str = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return outputs_str
    

def longt5_summarizer(model,model_id_or_path,text):
  tokenizer = AutoTokenizer.from_pretrained(model_id_or_path)
  inputs_dict = tokenizer(text, max_length=8192, return_tensors="pt")
  input_ids = inputs_dict.input_ids.to("cuda")
  predicted_abstract_ids = model.generate(input_ids)
  results = tokenizer.decode(predicted_abstract_ids[0], skip_special_tokens=True)
  return results

def led_summarizer(model,model_id_or_path,text):
  tokenizer = AutoTokenizer.from_pretrained(model_id_or_path)
  inputs_dict = tokenizer(text, max_length=8192, return_tensors="pt")
  input_ids = inputs_dict.input_ids.to("cuda")
  predicted_abstract_ids = model.generate(input_ids)
  results = tokenizer.decode(predicted_abstract_ids[0], skip_special_tokens=True)
  return results

# Define prediction function
def action_items_distil_bert(text_list):  
    
    # Load model
    if not os.path.exists(MODEL_FOLDER):
    # If the path does not exist, create the directory
      os.makedirs(MODEL_FOLDER)   
      os.system(f"git clone https://huggingface.co/asach/bert-action-items {MODEL_FOLDER}") 

    top_action_items = []

    if DEBUG == True:
      device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
      model_state_dict = torch.load(os.path.join(MODEL_FOLDER,"bert-action-items","model.pth"),map_location = device)
      tokenizer_action = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
      # Create model instance
      model_action = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2).to("cuda")
      # Load state dictionary into model
      model_action.load_state_dict(model_state_dict) 

    for text in text_list:
        model_action.eval()
        encoding = tokenizer_action.encode_plus(
            text,
            add_special_tokens=True,
            max_length=512,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        
        with torch.no_grad():
            outputs = model_action(input_ids, attention_mask=attention_mask)
            # Get predicted label
        pred_label = torch.argmax(outputs.logits).item()
        
        if pred_label == 1:
            top_action_items.append(text)
    
    return top_action_items