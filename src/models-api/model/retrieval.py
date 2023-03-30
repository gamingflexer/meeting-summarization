from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class ChatBot():
    def __init__(self,
                question,
                transcript,
                instruction = f'Instruction: given a dialog context, you need to responed.',
                model_name="microsoft/GODEL-v1_1-large-seq2seq"):

        self.dialog = question
        self.instruction = instruction
        self.knowledge = transcript
        self.model_name = model_name
        
    def load_chatbot(self):
        model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        return model,tokenizer

    def chatbot_response(self,tokenizer,model):
        if self.knowledge != '':
            self.knowledge = '[KNOWLEDGE] ' + self.knowledge

        dialog = ' EOS '.join(self.dialog)
        query = f"{self.instruction} [CONTEXT] {self.dialog} {self.knowledge}"
        print(query)
        input_ids = tokenizer(f"{query}", return_tensors="pt").input_ids
        outputs = model.generate(input_ids,max_length=128, min_length=8, top_p=0.9, do_sample=True)
        output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return output


# chat = ChatBot(question= "Hi what is your name?",transcript = "d")
# model,tokenizer = chat.load_chatbot()
# print(chat.chatbot_response(tokenizer,model))
"""
NOTE: This function is not used in the final version of the app. It is kept here for reference. | GODEL MODEL IS REPLCAED FOR THIS FUNCTION

import pandas as pd
import numpy as np
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
from transformers import pipeline
from utils import nlp


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

def chatbot_model_load(model_name = 'sentence-transformers/paraphrase-MiniLM-L6-v2'):
    model = AutoModel.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model,tokenizer

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
    
    return generate_answer(question,question_answering_pipeline,top_segments)

"""