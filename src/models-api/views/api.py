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
from views.summary import ModelSelectFromLength
from views.extras import summarize_conversation_extras

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
        data = request.get_json()

        #debug script
        if DEBUG:
            return {"data":
                        {
                            "summary":"Person 1 confides in Person 2 that their wife has discovered their affair with their secretary and is planning to divorce them. Person 2 expresses disappointment in Person 1's behavior, as they have been married for ten years, but Person 1 insists that the affair only lasted for two months and that they still love their wife. Person 2 promises to try to persuade the wife to reconsider the divorce, but questions whether Person 1 will be faithful in the future. Person 1 promises to be faithful forever.",
                            "extras" : {'sentiments': 'Neutral',
                                        'action_items': [],
                                        'decisions': [],
                                        'risks': [],
                                        'assumptions': [],
                                        'dependencies': ['PhD F said it depends, if you use "run command"'],
                                        'constraints': [],
                                        'tradeoffs': ['This could balance the load of the machines.',
                                        "This would help balance the workload of all the machines.'"],
                                        'open_questions': []},
                            "metadata" :{
                                            "email": ["test@gmail.com","test2@gmail.com"],
                                            "imp_dates": ["2020-12-12"],
                                            "phone_numbers": ["+91 23222322","23222322"],
                                            "human_names": ["name1","name2"],
                                            "addresses": "address1",
                                            "jargon_sentences":["jargon1","jargon2"],
                                            "action_items":["action1","action2"],
                                            "get_interactions_silence":{
                                                                        "interruptions":["interruption1","interruption2"],
                                                                        "silence":["duration1","duration2"]
                                                                        },
                                            "backchannels":['backchannel1','backchannel2'],
                                            "stats":[""],
                                            "meeting_category_assgined": "General",
                                            "roles_detected": {"speaker1": "test_role"},
                                            "meeting_description": "good meeting",
                                            "generated_title": "test title",
                                        },
                            "transcript_analysis" : "",
                            "models_used" : "allenai/led-base-16384",
                        },
                    }
                    
        # Configs
        # if data['translate'] == 1:  #hold on for now
        #     trancript_object = PreProcesssor(transcript_joined)
        #     transcript = pre_processor.tranlate_text()

        # backchannels_config = data.get('backchannels')
        # if backchannels_config == None:
        #     backchannels_config = 'nlp'

        # -------------------------------------------------------------------------------- #
        
        if data is None:
            return {"message": "No data provided"}, 400
        
        meeting_type = data['data'].get('meeting_type')

        if meeting_type == 'from_video_audio': # no speaker info
            transcript = data['data'].get('transcript') # this is a json
            transcript_joined = ""
            
        if meeting_type == 'from_transcript':
            transcript = data['data'].get('transcript') # this is a json but in text in request also
            transcript_joined = ""

        if meeting_type == 'from_extension':
            transcript = data['data'].get('transcript') # this is a string
            transcript_joined = ""


        """START HERE TO GET SUMMARY"""
        # formatted transcript preprocessor [NEED TO FORMAT !!]

        #Convert to DataFrame
        transcript_df = pd.DataFrame(transcript) ########## this is the transcript

        # -------------------------------------------------------------------------------- #

        #summary generation
        main_summary,models_used = ModelSelectFromLength(transcript_joined)
            
        #MAIN functions  ---> make a functions to convert into proper dataframe
        meta_data = processors_call_on_trancript(transcript_joined = transcript_joined, transcript_df = transcript_df, summary = main_summary)
        
        # #postprocessing
        post_processor = PostProcesssor(main_summary)
        clean_summary = post_processor.get_clean_summary()
        formatted_summary = post_processor.get_formatted_summary(clean_summary)

        return {"data":
                        {
                            "summary":formatted_summary,
                            "extras" : summarize_conversation_extras(transcript),
                            "metadata" :meta_data['meta_data'],
                            "transcript_analysis" : "",
                            "models_used" : models_used,
                        },
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