import whisper
import spacy

def wav_to_transcript(wav_file_path,model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(wav_file_path)
    return result

def transcript_to_summary(transcript):
    return transcript

def transcript_to_entities(transcript):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(transcript)
    return doc.ents