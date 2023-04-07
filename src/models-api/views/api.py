from werkzeug.utils import secure_filename
from flask_restful import Resource
from flask import request, json, render_template, make_response
import time
import os
from .models import wav_to_transcript, transcript_to_entities, audio_enhance
from model.retrieval import ChatBot
from model.highlights import get_highlights
from utils import allowed_file,extract_audio_from_any_file, format_server_time
from .helperFun import processors_call_on_trancript,PostProcesssor
from views.extras import summarize_conversation_extras
from views.transcript import convert_totranscript_json
from decouple import config
from config import LIVE_TRANSCRIPT_FILE
import pandas as pd
from views.summary import ModelSelectFromLength
from views.extras import summarize_conversation_extras
import ast

DEBUG = config('DEBUG', cast=bool)

if DEBUG == False:
    from views.transcript import TranscriptPreProcessor
    from views.helperFun import PreProcesssor,model_chat,tokenizer_chat
    # model_chat,tokenizer_chat = chat.load_chatbot()

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
        #debug script
        if DEBUG:
            return {
                    "transcript":"test_transcript"
                    }

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
            result_base = wav_to_transcript(audio_mp3_path,segments=False)
            print(" ---> Transcript generated")
            #result_denoised  = wav_to_transcript(new_audio_path,segments=True)
            return {
                    "transcript":result_base
                    }
    
class SummaryApi(Resource):
    
    def post(self):
        print("hii entered")
        
        data=request.get_data()
        data = data.decode("UTF-8",'surrogateescape')
        try:
                data = ast.literal_eval(str(data))
        except ValueError:
                data = json.loads(str(data))     
        print(data)
        """ Configs """
        
        # if data['translate'] == 1:  #hold on for now
        #     trancript_object = PreProcesssor(transcript_joined)
        #     transcript = pre_processor.tranlate_text()

        # backchannels_config = data.get('backchannels')
        # if backchannels_config == None:
        #     backchannels_config = 'nlp'

        # -------------------------------------------------------------------------------- #
        
        if data is None:
            return {"message": "No data provided"}, 400
        
        # meeting_type = data['data'].get('meeting_type')

        # if meeting_type == 'from_video_audio': # no speaker info
        #     transcript = data['data'].get('transcript') # this is a json
        #     transcript_joined = ""
            
        # if meeting_type == 'from_transcript':
        #     transcript = data['data'].get('transcript') # this is a json but in text in request also
        #     transcript_joined = ""

        # if meeting_type == 'from_extension':
        #     transcript = data['data'].get('transcript') # this is a string
        #     transcript_joined = ""


        """START HERE TO GET SUMMARY"""
        # formatted transcript preprocessor [NEED TO FORMAT !!]

        #Convert to DataFrame
        transcript_joined = data['data'].get('transcript') # this is a string
        segmented_df = pd.DataFrame((data['data'].get('segmented_df'))) ########## this is the segmented_df transcript

        highlight_json,segmented_title_df = get_highlights(segmented_df)

        transcript_df = segmented_df
        transcript_df.rename(columns={'text':'utterance'}, inplace=True)
        # -------------------------------------------------------------------------------- #

        #summary generation
        start_time = time.time()
        main_summary,models_used = ModelSelectFromLength(transcript_joined)
        print("\n--- Time to get the summary %s seconds ---\n" % (time.time() - start_time))

        #MAIN functions  ---> make a functions to convert into proper dataframe
        meta_data,df_updated = processors_call_on_trancript(transcript_joined = transcript_joined, transcript_df = transcript_df, summary = main_summary)
        transcript_json = convert_totranscript_json(df_updated)

        # #postprocessing
        post_processor = PostProcesssor(main_summary)
        clean_summary = post_processor.get_clean_summary()
        formatted_summary = post_processor.get_formatted_summary(clean_summary)
        print("\n--- TOTAL TIME %s seconds ---\n" % (time.time() - start_time))
        
        try:
            final_summary = formatted_summary
        except NameError:
            try:
                final_summary = clean_summary
            except:
                final_summary = main_summary

        return {"data":
                        {
                            "summary":final_summary,
                            "extras" : summarize_conversation_extras(transcript_joined),
                            "metadata" :meta_data['meta_data'],
                            "models_used" : models_used,
                            "highlights" : highlight_json,
                            "transcript" : transcript_json,
                        }
                    }
        

class EntitiesApi(Resource):

    def post(self):
        data = request.get_json()
        entites = transcript_to_entities(data['transcript'])
        return {"result": entites}, 200

class ChatApi(Resource):

    def post(self):
        data = request.get_json()
        chat = ChatBot(question= data['data']['question'],transcript = data['data']['document'])
        response = chat.chatbot_response(tokenizer_chat,model_chat)
        return {"data": response}, 200
    
class LiveChatApi(Resource):
    
    def get(self):
        with open(LIVE_TRANSCRIPT_FILE, 'r') as file:
            data = max(file.read().split("|"), key=len)
            
        return {"data": data.replace('\n', " ")}, 200

    def post(self):
        data=request.get_data()
        data = data.decode("UTF-8",'surrogateescape')
        try:
            data = ast.literal_eval(str(data))
        except ValueError:
            data = json.loads(str(data))
                
        transcript = data['transcript']
        
        print(LIVE_TRANSCRIPT_FILE)
        with open(LIVE_TRANSCRIPT_FILE, 'a') as file:
            file.write(transcript + "|")
            
        return {"data": "Added"}, 200