from transformers import pipeline

def bart_summarize(text,hub_model_id):
    summarizer = pipeline("summarization", model="mikeadimech/longformer-qmsum-meeting-summarization")
    summary = summarizer(text)
    return summary[0]['summary_text']