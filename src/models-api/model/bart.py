from transformers import pipeline

def bart_summarize(text,hub_model_id):
    summarizer = pipeline("summarization", model=hub_model_id)
    summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
    return summary[0]['summary_text']