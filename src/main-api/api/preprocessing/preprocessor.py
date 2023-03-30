# Transcipt Types
import os
import re
import json
import pandas as pd
from langdetect import detect
from .utils import (transcript_html_to_dataframe, 
                   transcript_to_dataframe, 
                   transcript_webvtt_to_dataframe, 
                   json_zoom_transcript_file,
                   segment_transcript,
                   duration_from_transcript)

def any_transcript_to_dataframe(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.html':
        df = transcript_html_to_dataframe(file_path)
        return df
    
    elif file_extension == '.txt':
        df = transcript_to_dataframe(file_path)
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
                print(e,"\nException : Transcript Conversion Exception\n")
                return pd.read_json(file_path)
        return df
    
    elif file_extension == '.vtt':
        df = transcript_webvtt_to_dataframe(file_path)
        
    elif file_extension == '.csv':
        df = pd.read_csv(file_path)
        
    else:
        raise Exception(' \n IMP ERROR :File extension not supported \n', file_extension)
    
    """PREPROCESSING FUNCTIONS"""
    
    df_grouped = pd.DataFrame()
    df_grouped['speaker_dialogue'] = df['speaker'] + ': ' + df['text']
    speaker_dialogue = df_grouped['speaker_dialogue'].str.cat(sep='\n')
    segmented_df = segment_transcript(df)
    durations = duration_from_transcript(segmented_df)
    attendeces_count = len(df['speaker'].unique())
    print(segmented_df,speaker_dialogue,durations,attendeces_count)
    return segmented_df,speaker_dialogue,durations,attendeces_count


def identify_meeting_link(meeting_link):
    # Check if link is for Google Meet
    google_meet_pattern = r'https:\/\/meet.google.com\/[a-z]+-[a-z]+-[a-z]+'
    if re.match(google_meet_pattern, meeting_link):
        return 'Google Meet'

    # Check if link is for Zoom
    zoom_pattern = r'https:\/\/[a-z]+\.zoom\.us\/[a-z]+\/[0-9a-zA-Z?=&]+'
    if re.match(zoom_pattern, meeting_link):
        return 'Zoom'

    # Check if link is for Microsoft Teams
    teams_pattern = r'https:\/\/teams\.microsoft\.com\/[a-z]+\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+\/[0-9a-zA-Z?=&]+'
    if re.match(teams_pattern, meeting_link):
        return 'Teams'

    # Return None if link is not recognized
    return ''

def detect_language(text):
    try:
        language = detect(text)
    except:
        language = 'unknown'
    return str(language)