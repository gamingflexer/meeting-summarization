import nltk

def clean_summary(summary):
    tokens = nltk.word_tokenize(summary)
    pos_tags = nltk.pos_tag(tokens)

    # Check for any contradictory statements
    for i in range(len(pos_tags)-1):
        if pos_tags[i][1] == 'JJ' and pos_tags[i+1][0] == 'not':
            print("Warning: Contradictory statement detected.")
    
    new_summary = ' '.join([word for word in summary.split() if word.lower() not in key_words])
    return new_summary

def format_summary(summary):
    # Split the summary into sentences
    sentences = summary.split(". ")

    # Add line breaks after each sentence and indent with bullet points
    formatted_summary = "\n".join(["• " + sentence.strip() for sentence in sentences])

    return formatted_summary