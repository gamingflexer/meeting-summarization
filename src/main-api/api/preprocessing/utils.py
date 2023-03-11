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

