from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import spacy

# Load the spaCy model for English language
nlp = spacy.load("en_core_web_sm")

# Define the function for extracting sentences with highest cosine similarity to the topic
def extract_sentences(text, n_sentences=5, n_topics=3):
    # Initialize the CountVectorizer for text preprocessing
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])

    # Initialize the LDA model for topic modeling
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)

    # Extract the topic-word distribution and word-document distribution
    topic_word_dist = lda.components_ / lda.components_.sum(axis=1)[:, np.newaxis]
    doc_topic_dist = lda.transform(X)

    # Extract the top sentences based on cosine similarity to the topic
    sentences = [sent for sent in nlp(text).sents]
    sentence_vectors = []
    for sent in sentences:
        sent_vector = np.zeros((n_topics,))
        for token in sent:
            if token.text in vectorizer.vocabulary_:
                sent_vector += topic_word_dist[:, vectorizer.vocabulary_[token.text]] * doc_topic_dist[0]
        sentence_vectors.append(sent_vector)
    sentence_vectors = np.array(sentence_vectors)
    sim_matrix = cosine_similarity(sentence_vectors)
    sim_scores = np.sum(sim_matrix, axis=0)
    top_sentence_indices = sim_scores.argsort()[-n_sentences:][::-1]
    top_sentences = [sentences[i].text.strip() for i in top_sentence_indices]

    return top_sentences

# extract_sentence = extract_sentences(transcript2)
# extract_sentence joined_sentences = ' '.join(extract_sentence)
#thanks everyone
#2 in context follows q and answer or inside one