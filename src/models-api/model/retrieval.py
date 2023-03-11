import pandas as pd
import numpy as np
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
from __init__ import nlp

# Preprocess transcript and summary data
def preprocess_text(text):
    # Remove punctuation and stop words
    doc = nlp(text)
    tokens = [token for token in doc if not token.is_punct and not token.is_stop]
    return ' '.join(str(token) for token in tokens)

# ChatBot Functions
def compute_embeddings(texts,tokenizer,model):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    outputs = model(**inputs).last_hidden_state
    return outputs.mean(dim=1).detach().numpy()

# Generate answers to questions using the retrieved transcript segments
def generate_answer(question,question_answering_pipeline,top_segments):
    answers = []
    for segment in top_segments:
        answer = question_answering_pipeline(question=question, context=segment)
        answers.append(answer)
    best_answer = max(answers, key=lambda x: x['score'])
    return best_answer['answer']

def chatbot_response(question, transcript, summary, tokenizer, model):
    
    # Load transcript and summary data
    transcript_df = pd.DataFrame({"text":transcript}, index=[0])
    summary_df = pd.DataFrame({"summary":summary}, index=[0])

    transcript_df['processed_text'] = transcript_df['text'].apply(preprocess_text)
    summary_df['processed_summary'] = summary_df['summary'].apply(preprocess_text)

    transcript_embeddings = compute_embeddings(transcript_df['processed_text'][0],tokenizer,model)
    summary_embedding = compute_embeddings(summary_df['processed_summary'][0],tokenizer,model)[0]

    # Compute similarity scores between summary and each transcript segment
    similarity_scores = cosine_similarity(summary_embedding.reshape(1, -1), transcript_embeddings)[0]

    # Retrieve top N transcript segments based on similarity score
    N = 5
    top_segments_indices = np.argsort(similarity_scores)[-N:][::-1]
    top_segments = transcript_df.iloc[top_segments_indices]['text'].tolist()

    # Initialize transformer-based pipeline for generating answers
    question_answering_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", tokenizer="distilbert-base-cased")
    
    answer = generate_answer(question,question_answering_pipeline,top_segments)
    return answer