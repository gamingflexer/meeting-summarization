import json
import pandas as pd
from bs4 import BeautifulSoup
import re

def json_zoom_transcript_file(file_path):
    with open(file_path, 'r') as f:
        transcript = json.load(f)['recording_transcript']
    rows = []
    for page in transcript['pages']:
        page_number = page['page_number']
        for content in page['content']:
            row = {
                'page_number': page_number,
                'speaker': content['speaker'],
                'start_time': content['start_time'],
                'duration': content['duration'],
                'text': content['text']
            }
            rows.append(row)
    return pd.DataFrame(rows)


def extract_timestamps_and_text_from_html(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    timed_text_divs = soup.find_all('div', {'class': 'timed-text'})

    timestamps = []
    speakers = []
    texts = []

    for timed_text_div in timed_text_divs:
        timestamp_div = timed_text_div.find('div', {'class': 'timestamp'})
        speaker_div = timed_text_div.find('div', {'class': 'speaker'})
        text_div = timed_text_div.find('div', {'class': 'text'})

        if timestamp_div and speaker_div and text_div:
            timestamp_str = re.search('\[(.*?)\]', timestamp_div.text).group(1)
            speaker_str = speaker_div.text
            text_str = text_div.text

            timestamps.append(timestamp_str)
            speakers.append(speaker_str)
            texts.append(text_str)

    data = {'timestamp': timestamps, 'speaker': speakers, 'text': texts}
    df = pd.DataFrame(data)
    return df


def transcript_html_to_dataframe(file_path):
    try:
        with open(file_path) as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        timed_texts = soup.find_all('div', {'class': 'timed-text'})
        
        data = []
        for timed_text in timed_texts:
            timestamp = timed_text.find('div', {'class': 'timestamp'}).text.strip('[]')
            speaker = timed_text.find('div', {'class': 'speaker'}).text.strip()
            text = timed_text.find('div', {'class': 'text'}).text.strip()
            data.append([timestamp, speaker, text])
        
        df = pd.DataFrame(data, columns=['Timestamp', 'Speaker', 'Text'])
        return df
    except:
        df = extract_timestamps_and_text_from_html(file_path)
        
def transcript_to_dataframe(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    time_stamps = []
    speakers = []
    texts = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        time_stamp, text = line.split(']', 1)
        speaker, text = text.split(':', 1)
        time_stamp = time_stamp[1:]
        
        time_stamps.append(time_stamp)
        speakers.append(speaker)
        texts.append(text.strip())
    
    df = pd.DataFrame({
        'time_stamp': time_stamps,
        'speaker': speakers,
        'text': texts
    })
    
    return df


def transcript_webvtt_to_dataframe(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    rows = []
    for i in range(len(lines)):
        if ' --> ' in lines[i]:
            start_time, end_time = lines[i].strip().split(' --> ')
            text = lines[i+1].strip().replace(':', ': ')
            rows.append({'start_time': start_time, 'end_time': end_time, 'text': text})
    df = pd.DataFrame(rows)
    return df

def segment_transcript(df):
    # Define the keywords for each section
    with open('./data/start_meet_keywords.txt', 'r') as f:
        start_keywords = [line.strip() for line in f.readlines()]
    with open('./data/main_context_keywords.txt', 'r') as f:
        context_keywords = [line.strip() for line in f.readlines()]
    with open('./data/end_meet_keywords.txt', 'r') as f:
        end_keywords = [line.strip() for line in f.readlines()]

    # Initialize the section markers
    start_marker = None
    end_marker = None

    # Iterate through the lines and look for the keywords
    for i, row in df.iterrows():
        text = row['text']
        # Check for start keyword
        if not start_marker and any(keyword in text.lower() for keyword in start_keywords):
            start_marker = i

        # Check for end keyword
        if not end_marker and any(keyword in text.lower() for keyword in end_keywords):
            end_marker = i

    # Create the segments based on the markers
    start_segment = df.loc[:start_marker-1] if start_marker is not None else None
    end_segment = df.loc[end_marker:] if end_marker is not None else None
    
    main_context = df.loc[start_marker:end_marker-1] if start_marker is not None and end_marker is not None else None
    
    # Add new column to each segment
    if start_segment is not None:
        start_segment['main_timestamps'] = 'start'
    if end_segment is not None:
        end_segment['main_timestamps'] = 'end'
    if main_context is not None:
        main_context['main_timestamps'] = 'main_context'
    
    # Combine the segments into a single DataFrame
    segments = pd.concat([df for df in [start_segment, main_context, end_segment] if df is not None])
    
    return segments

def duration_from_transcript(df):
    try:
        df['time'] = pd.to_timedelta(df['time_stamp'])
        # Calculate the end time for each speaker
        df['end_time'] = df['time_stamp']
        # Shift the end time by one row to get the start time for each speaker
        df['start_time'] = df['end_time'].shift()
        # Calculate the duration for each speaker
        df['duration'] = df['end_time'] - df['start_time']
    except Exception as e:
        print("ERROR !! : ",e)
        if str(df['start_time'][0]) == "nan":
            start_time = "00.000"
            return {"start_time":start_time,"end_time":df['end_time'][df.index[-1]]}
        return {"start_time":df['start_time'][0],"end_time":df['end_time'][df.index[-1]]}
    
    if str(df['start_time'][0]) == "nan":
            start_time = "00.000"
            return {"start_time":start_time,"end_time":df['end_time'][df.index[-1]]}
    return {"start_time":df['start_time'][0],"end_time":df['end_time'][df.index[-1]]}