"""
NOTE: This function is not used in the final version of the app. It is kept here for reference. | GODEL MODEL IS REPLCAED FOR THIS FUNCTION

import re
from textblob import TextBlob

# NOT USED
def top_segmentor_v0_1(transcript):
    # Split transcript into sentences
    sentences = re.split('[.!?]', transcript)

    # Use TextBlob to detect the topic of each sentence
    topics = {}
    for sentence in sentences:
        if sentence.strip() != '':
            blob = TextBlob(sentence)
            topic = blob.sentiment.subjectivity
            if topic not in topics:
                topics[topic] = [sentence]
            else:
                topics[topic].append(sentence)

    # Combine sentences into sections based on topic similarity
    sections = {}
    for i, (topic, sentences) in enumerate(topics.items()):
        section = ' '.join(sentences)
        sections[f'Section {i+1}'] = section

    return sections

"""