# Meeting Summarization with Deep Learning

In the work from home scenario prevailing over the last 18 months and with hybrid working picking steam, most Official meetings have been or will be conducted virtually.
While MICROSOFT TEAMS / Google Meet / Zoom do provide a feature to download TRANSCRIPT, it does not summarise the meeting.

Problem Dimensions

- Parse the Transcript to figure out many attendees were there in the meeting.
- Duration of the meeting
- Most importantly produce a gist / summary of the meeting
- List the Action items if they are specifically called out.
- Incase where Transcript is not available, you will have to additionally work on converting SPEECH to TEXT

## Introduction

Project features Implementated are 

- [x] Speech to text
- [x] Text summarization
- [x] Action items
- [x] Meeting duration
- [x] Meeting attendees 
Many More ...

## Requirements

- Python 3.6+
- Good GPU (Nvidia GTX 1080 or better) to run all models in parallel

## Usage in Development

#### Start the main application

```
git clone https://github.com/gamingflexer/meeting-summarization-api.git
cd src/main-api
pip3 install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```

API SERVER

`python manage.py runserver`

Chatbot

```
python manage.py tailwind init
python manage.py tailwind install
```

```
python manage.py runserver 0.0.0.0:8001
redis-server
python manage.py tailwind start
```

#### Start the meeting summarization api [GCP]

```
cd src/models-api
python __init__.py
```

## Usage in Production

Some extra steps are required to run the application in production and development. run this inside `models-api` folder

```
pip install git+https://github.com/openai/whisper.git --no-deps
python -m spacy download en_core_web_sm
pip install -U scikit-learn scipy matplotlib
git clone https://github.com/maxent-ai/converse.git && cd converse && pip install -e . && cd ..
sudo apt install ffmpeg
sudo apt-get install libsndfile1-dev
```

## Comman Issues 

- `PermissionError:` sudo chmod -R 777 path of the media folder`

## Project Structure

### Collaborators

- [Om Surve](asach.co)
- [Kunal Wagh]()
- [Yash Wakekar]()
- [HItesh Meta]()