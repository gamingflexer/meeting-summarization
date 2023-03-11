from transformers import pipeline
from transformers import AutoTokenizer
from utils import sentiment_reverser

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
      summary_ids = model.generate(inputs["input_ids"])
      return tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    except IndexError:
      print(f"\n ERROR: Model not compatible with the tokeinizer or no tokenizer exits at huggingface {model_id_or_path}")
      return ""

def bart_title_summarizer(model,model_path,text):
    try:
      tokenizer = AutoTokenizer.from_pretrained(model_path)
    except OSError:
      tokenizer = AutoTokenizer.from_pretrained("")    
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
    
