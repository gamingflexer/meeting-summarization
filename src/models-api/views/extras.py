import re
import spacy
from spacy.matcher import Matcher
from collections import defaultdict,Counter

# load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load('en_core_web_sm')

def extract_speakers(text):
    # extract speakers from conversation
    speakers = defaultdict(int)
    lines = text.split("\n")
    for line in lines:
        if ":" in line:
            speaker, _ = line.split(":", 1)
            speakers[speaker.strip()] += 1
    return dict(speakers)


def extract_sentiment(text):
    # extract sentiment of each speaker's statements
    # sentiment analysis with TextBlob
    from textblob import TextBlob

    lines = text.split("\n")
    sentiment_dict = {}
    for line in lines:
        if ":" in line:
            speaker, statement = line.split(":", 1)
            blob = TextBlob(statement)
            sentiment_polarity = blob.sentiment.polarity
            if sentiment_polarity > 0:
                sentiment = "Positive"
            elif sentiment_polarity < 0:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            sentiment_dict[line] = sentiment
    return sentiment_dict


def extract_actions(text):
    # extract action items or next steps discussed during conversation
    matcher = Matcher(nlp.vocab)
    pattern = [{'POS': 'VERB'}, {'POS': 'ADV', 'OP': '?'}, {'POS': 'PART', 'OP': '?'}, {'POS': 'VERB', 'OP': '?'},
               {'POS': 'DET', 'OP': '?'}, {'POS': 'NOUN', 'OP': '+'}]
    matcher.add("Action", None, pattern)
    doc = nlp(text)
    actions = []
    for match_id, start, end in matcher(doc):
        actions.append(doc[start:end].text)
    return actions


def extract_decisions(text):
    # extract decisions made during conversation
    matcher = Matcher(nlp.vocab)
    pattern = [{'LEMMA': 'decide'}, {'POS': 'VERB', 'OP': '*'}, {'POS': 'DET', 'OP': '?'}, {'POS': 'NOUN', 'OP': '+'}]
    matcher.add("Decision", [pattern])
    doc = nlp(text)
    decisions = []
    for match_id, start, end in matcher(doc):
        decisions.append(doc[start:end].text)
    return decisions

nlp = spacy.load('en_core_web_sm')

def extract_topics_speakers_sentiments(conversation):
    topics = defaultdict(list)
    speakers = []
    sentiments = defaultdict(list)
    
    for line in conversation.split('\n'):
        if 'Discussion Title' in line:
            topics['Title'].append(line.split(':')[-1].strip())
        elif 'Transcript' in line:
            topics['Transcript'].append(line.split(':')[-1].strip())
        elif ':' in line:
            speaker, utterance = line.split(':', maxsplit=1)
            speakers.append(speaker)
            doc = nlp(utterance)
            sentiment = doc.sentiment.polarity
            if sentiment > 0:
                sentiment_label = 'Positive'
            elif sentiment < 0:
                sentiment_label = 'Negative'
            else:
                sentiment_label = 'Neutral'
            sentiments[speaker].append(sentiment_label)
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    topics['People Mentioned'].append(ent.text)
                elif ent.label_ == 'ORG':
                    topics['Organizations Mentioned'].append(ent.text)
                elif ent.label_ == 'GPE':
                    topics['Locations Mentioned'].append(ent.text)
                    
    topics['Unique Topics Mentioned'] = list(set(topics['People Mentioned'] + 
                                                 topics['Organizations Mentioned'] + 
                                                 topics['Locations Mentioned']))
    
    return topics, list(set(speakers)), sentiments

def extract_risks(conversation):
    # Regular expression pattern to match any sentence containing the word "risk"
    risk_pattern = re.compile(r"\b(?i)risk(s)?\b")

    risks = []
    for sentence in conversation:
        # Check if the sentence contains the word "risk"
        if risk_pattern.search(sentence):
            # Add the sentence to the list of risks
            risks.append(sentence)

    return risks

def extract_assumptions(conversation):
    """Extracts any assumptions made during the conversation"""
    assumptions = []
    for line in conversation.split('\n'):
        if 'assume' in line.lower() or 'assumption' in line.lower():
            assumptions.append(line)
    return assumptions


def extract_dependencies(conversation):
    """Extracts any dependencies discussed during the conversation"""
    dependencies = []
    for line in conversation.split('\n'):
        if 'depend' in line.lower() or 'dependency' in line.lower():
            dependencies.append(line)
    return dependencies


def extract_constraints(conversation):
    """Extracts any constraints discussed during the conversation"""
    constraints = []
    for line in conversation.split('\n'):
        if 'constraint' in line.lower() or 'restrict' in line.lower():
            constraints.append(line)
    return constraints


def extract_tradeoffs(conversation):
    """Extracts any trade-offs discussed during the conversation"""
    tradeoffs = []
    for line in conversation.split('\n'):
        if 'trade-off' in line.lower() or 'balance' in line.lower():
            tradeoffs.append(line)
    return tradeoffs


def extract_open_questions(conversation):
    """Extracts any open questions or uncertainties discussed during the conversation"""
    open_questions = []
    for line in conversation.split('\n'):
        if '?' in line:
            open_questions.append(line)
    return open_questions

def summarize_conversation_extras(conversation):
    
    # Initialize variables for tracking conversation data
    statements = []
    sentiments = []
    action_items = []
    decisions = []
    risks = []
    assumptions = []
    dependencies = []
    constraints = []
    tradeoffs = []
    open_questions = []

    # Process the conversation text with spaCy
    doc = nlp(conversation)

    # Iterate over each sentence in the document
    for sent in doc.sents:
        
        # Extract the speaker and statement from the sentence
        speaker, statement = extract_speaker_and_statement(sent.text)
        statements.append(statement)
        
        # Extract the sentiment of the statement
        sentiment = analyze_sentiment(statement)
        sentiments.append(sentiment)
        
        
        # Extract any action items discussed in the statement
        statement_action_items = extract_action_items(statement)
        action_items.extend(statement_action_items)
        
        # Extract any decisions made in the statement
        statement_decisions = extract_decisions(statement)
        decisions.extend(statement_decisions)
        
        # Extract any risks or potential issues discussed in the statement
        statement_risks = extract_risks(statement)
        risks.extend(statement_risks)
        
        # Extract any assumptions made in the statement
        statement_assumptions = extract_assumptions(statement)
        assumptions.extend(statement_assumptions)
        
        # Extract any dependencies discussed in the statement
        statement_dependencies = extract_dependencies(statement)
        dependencies.extend(statement_dependencies)
        
        # Extract any constraints discussed in the statement
        statement_constraints = extract_constraints(statement)
        constraints.extend(statement_constraints)
        
        # Extract any trade-offs discussed in the statement
        statement_tradeoffs = extract_tradeoffs(statement)
        tradeoffs.extend(statement_tradeoffs)
        
        # Extract any open questions or uncertainties discussed in the statement
        statement_open_questions = extract_open_questions(statement)
        open_questions.extend(statement_open_questions)
    
    # Summarize the conversation data
    sentiment_final = Counter(sentiments).most_common(1)[0][0] 
    summary = {
        "sentiments": sentiment_final,
        "action_items": action_items,
        "decisions": decisions,
        "risks": risks,
        "assumptions": assumptions,
        "dependencies": dependencies,
        "constraints": constraints,
        "tradeoffs": tradeoffs,
        "open_questions": open_questions
    }
    
    return summary


def extract_speaker_and_statement(sentence):
    # split the sentence on the first occurrence of ":"
    parts = sentence.split(":", 1)
    if len(parts) == 2:
        # extract the speaker and statement
        speaker = parts[0].strip()
        statement = parts[1].strip()
    else:
        # if there is no ":", assume the speaker is "Unknown"
        speaker = "Unknown"
        statement = parts[0].strip()
    return speaker, statement


def analyze_sentiment(statement):
    # perform sentiment analysis on the statement using spaCy
    doc = nlp(statement)
    sentiment = doc.sentiment
    if sentiment > 0:
        return "Positive"
    elif sentiment < 0:
        return "Negative"
    else:
        return "Neutral"


def extract_action_items(conversation):
    # initialize empty list to store action items
    action_items = []

    # loop through each sentence in the conversation
    for sentence in conversation:
        # check if sentence contains keywords indicating an action item
        if "action item" in sentence.lower() or "next step" in sentence.lower():
            # remove any leading/trailing whitespace and punctuation from sentence
            sentence = sentence.strip()
            sentence = re.sub('[^\w\s]', '', sentence)

            # split sentence into individual words
            words = sentence.split()

            # loop through each word and remove stopwords and punctuation
            filtered_words = []
            for word in words:
                if word.lower() not in stopwords.words("english") and word.isalnum():
                    filtered_words.append(word)

            # join filtered words back into a sentence
            filtered_sentence = " ".join(filtered_words)

            # add filtered sentence to list of action items
            action_items.append(filtered_sentence)

    # return list of action items
    return action_items
