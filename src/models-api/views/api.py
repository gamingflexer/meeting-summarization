from werkzeug.utils import secure_filename
from flask_restful import Resource
from flask import request, json, render_template, make_response
import os
from .models import wav_to_transcript, transcript_to_entities, audio_enhance
from model.retrieval import ChatBot
from utils import allowed_file,extract_audio_from_any_file, format_server_time
from .helperFun import processors_call_on_trancript

from decouple import config
from config import MODEL_FOLDER
from views.models import ModelSelect
from views.helperFun import PreProcesssor

DEBUG = config('DEBUG', cast=bool)

if DEBUG == False:
    from views.transcript import TranscriptPreProcessor
    model_chat,tokenizer_chat = chat.load_chatbot()

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    

class IndexPage(Resource):
    def __init__(self):
        pass

    def get(self):
        context = { 'server_time': format_server_time() }
        return make_response(render_template('index.html', context=context))

class AudioApi(Resource):
    def post(self):
        if 'file' not in request.files:
            resp = ({'message' : 'No file part in the request'})
            return resp
        file = request.files['file']
        if file.filename == '':
            resp = ({'message' : 'No file selected for uploading'})
            return resp
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            print(" ---> File saved")
            audio_mp3_path = extract_audio_from_any_file(os.path.join(UPLOAD_FOLDER, filename))
            print(" ---> Audio extracted")
            #new_audio_path = audio_enhance(audio_mp3_path)
            result_base = wav_to_transcript(audio_mp3_path,segments=True)
            print(" ---> Transcript generated")
            #result_denoised  = wav_to_transcript(new_audio_path,segments=True)
            return {
                    "transcript":result_base
                    }
    
class SummaryApi(Resource):
    
    def post(self):
        data = request.get_json()
        
        if data is None:
            return {"message": "No data provided"}, 400
        
        meeting_type = data['data'].get('meeting_type')
        
        if meeting_type == 'from_video_audio': # no speaker info
            transcript = data['data'].get('transcript') # this is a json
            transcript_joined = ""
            data_json = processors_call_on_trancript(data)
            return data_json
            
        if meeting_type == 'from_transcript':
            transcript = data['data'].get('transcript') # this is a json but in text in request also
            data_json = processors_call_on_trancript(data)
            return data_json

        if meeting_type == 'from_extension':
            transcript = data['data'].get('transcript') # this is a string
            data_json = processors_call_on_trancript(data)
            return data_json


        """START HERE TO GET SUMMARY"""

        # #get entites
        # df_formatted = 
        # transcript_analysis = TranscriptPreProcessor(transcript = df_formatted) 


        # #preprocessing
        # pre_processor = PreProcesssor(transcript) # unformatted simple trancript
        # email,date,phone_numbers,human_name,addresses = pre_processor.get_entites()
        # jargon_sentences = pre_processor.get_jargon_sentences()
        # get_meeting_structure = pre_processor.get_meeting_structure()

        # if data['translate'] == 1: #hold on for now
        #     transcript = pre_processor.tranlate_text()
        #preprocessing
        pre_processor = PreProcesssor(transcript)
        email,date,phone_numbers,human_name,addresses = pre_processor.get_entites()
        jargon_sentences = pre_processor.get_jargon_sentences()
        get_meeting_structure = pre_processor.get_meeting_structure()
        
        # Configs
        if data['translate'] == 1:
            transcript = pre_processor.tranlate_text()
        
        backchannels_config = data.get('backchannels')
        if backchannels_config == None:
            backchannels_config = 'nlp'
            
            
        #MAIN functions  ---> make a functions to convert into proper dataframe
        #transcript_analysis = TranscriptPreProcessor(transcript = transcript, backchannels=backchannels_config)
        
        #summary generation
        new_model = ModelSelect(modelname = 'bart',model_id_or_path= 'knkarthick/MEETING_SUMMARY',text = transcript,max_new_tokens=200)
        model = new_model.load_model()
        results = new_model.generate_summary(model)
        
        # #postprocessing
        post_processor = PostProcesssor(main_summary)
        clean_summary = post_processor.get_clean_summary()
        formatted_summary = post_processor.get_formatted_summary(clean_summary)

        return {"data":[
                        {"summary":results},
                        ]
                    }
        
class EntitiesApi(Resource):
    def post(self):
        data = request.get_json()
        entites = transcript_to_entities(data['transcript'])
        return {"result": entites}, 200

class ChatApi(Resource):

    def post(self):
        data = request.get_json()
        chat = ChatBot(question= data['question'],transcript = data['document'])
        response = chat.chatbot_response(tokenizer_chat,model_chat)
        return {"data": response}, 200