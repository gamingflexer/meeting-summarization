from config import media_path
from decouple import config
import requests
import urllib
import json
import os

# url_sumarization = config("URL_SUMMARIZATION")

#audio links?
def summarization_function(file_path_or_link, file=False):
    if file == False:
        urllib.request.urlretrieve(file_path_or_link, os.path.join(media_path,"audio","transcript.txt"))
        print("file downloaded")
    #some pre-processing step
    
    data = (open(os.path.join(file_path_or_link), 'rb').read()).decode('utf-8')
    
    with open(os.path.join(media_path,"test.html"), "w") as e:
        for lines in data.readlines():
            line = lines.split(":")
            e.write("<pre>" + "<b>" + line[0]  +"</b> :" +  line[1] + "</pre>\n")
    hocr_transcript = open(os.path.join(media_path,"test.html"), "r").read()
        
    try:
        response = requests.post(url_sumarization, 
                                data=json.dumps({"transcript":data}), 
                                headers={"Content-Type": "application/json"})
        response.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("Down")
    except requests.exceptions.HTTPError:
        print("4xx, 5xx")
    summary =  (response.json())['summary']
    
    return str(summary),hocr_transcript