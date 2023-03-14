from werkzeug.utils import secure_filename
from flask_restful import Resource
from flask import request, json
import os

from .models import wav_to_transcript, transcript_to_entities, audio_enhance
from utils import allowed_file,extract_audio_from_any_file

from decouple import config
from config import MODEL_FOLDER
from views.models import ModelSelect
from views.helperFun import PreProcesssor,PostProcesssor

DEBUG = config('DEBUG', cast=bool)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class AudioApi(Resource):
    def post(self):
        if 'file' not in request.files:
            resp = ({'message' : 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = request.files['file']
        if file.filename == '':
            resp = ({'message' : 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            if DEBUG:
                return ({"summary":"summary"}),200
            audio_mp3_path = extract_audio_from_any_file(os.path.join(UPLOAD_FOLDER, filename))
            new_audio_path = audio_enhance(audio_mp3_path)
            result_base = wav_to_transcript(audio_mp3_path)
            result_denoised  = wav_to_transcript(new_audio_path)
            return {
                    "transcript":[result_base,result_denoised]
                    }
    
class SummaryApi(Resource):
    def post(self):
        data = request.get_json()
        transcript = data.get('transcript')
        
        """START HERE TO GET SUMMARY"""
        #preprocessing
        pre_processor = PreProcesssor(transcript)
        email,date,phone_numbers,human_name,addresses = pre_processor.get_entites()
        jargon_sentences = pre_processor.get_jargon_sentences()
        get_meeting_structure = pre_processor.get_meeting_structure()
        if data['translate'] == 1:
            transcript = pre_processor.tranlate_text()
            
        #summary generation
        new_model = ModelSelect(data['model'],transcript,max_new_tokens=200)
        model = new_model.load_model()
        results = new_model.generate_summary(model)
        
        #postprocessing
        post_processor = PostProcesssor(results)
        clean_summary = post_processor.get_clean_summary()
        formatted_summary = post_processor.get_formatted_summary(clean_summary)
        
        #return summary
        return {"summary": formatted_summary,
                "meta_data":{"email":email,
                             "dates":date,
                             "phone_numbers":phone_numbers,
                             "human_names":human_name,
                             "addresses":addresses,
                             "jargon_sentences":jargon_sentences,
                             "meeting_structure":get_meeting_structure}
                }, 200
    
class EntitiesApi(Resource):
    def post(self):
        data = request.get_json()
        entites = transcript_to_entities(data['transcript'])
        return {"result": entites}, 200