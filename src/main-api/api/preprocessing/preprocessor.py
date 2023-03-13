# Transcipt Types
import os
import json
import pandas as pd
from utils import (transcript_html_to_dataframe, 
                   transcript_to_dataframe, 
                   transcript_webvtt_to_dataframe, 
                   json_zoom_transcript_file)

def any_transcript_to_dataframe(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.html':
        df = transcript_html_to_dataframe(file_path)
        return df
    elif file_extension == '.txt':
        try:
            df = transcript_to_dataframe(file_path)
        except Exception as e:
            print(e,"\EXCEPTION : Transcript Conversion Exception\n")
            return pd.read_csv(file_path, sep='\t', header=None)
        return df
    elif file_extension == '.json':
        with open(file_path, "r") as f:
            data = json.load(f)
        if 'results' in data:
            df = pd.json_normalize(data, record_path=["results", "alternatives"])
        elif "meeting_id" in data:
            df = json_zoom_transcript_file(file_path)
        else:
            try:
                df = pd.json_normalize(data)
            except Exception as e:
                print(e,"\EXCEPTION : Transcript Conversion Exception\n")
                return pd.read_json(file_path)
            
        return df
    elif file_extension == '.vtt':
        df = transcript_webvtt_to_dataframe(file_path)
        return df
    else:
        return 'unknown'
