import whisper

def wav_to_transcript(wav_file_path,model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(wav_file_path)
    return result

def transcript_to_summary(transcript):
    return transcript