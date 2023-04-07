from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from drf_yasg import openapi

from api.serializers import User_info_Serializers,Summary_Serializers,FileSerializer,CalendarEventSerializer
from api.models import User_info,Summary
from authentication.models import User
from .permissions import user_auth_required
from config import base_path_file
from authentication.models import User
from decouple import config
from utils import txt_to_pdf

from .utility import  preprocess_hocr
from .preprocessing.preprocessor import any_transcript_to_dataframe,identify_meeting_link,detect_language,start_end_from_transcript
from .global_constant import *
import datetime
import requests
import json
import os

from django.core.exceptions import ObjectDoesNotExist
from firebase_admin import credentials,auth
import firebase_admin

DEBUG = config('DEBUG', cast=bool)
URL_MICRO = config('URL_MICRO')

cred = credentials.Certificate(settings.FIREBASE_CONFIG_PATH)
firebase_app=firebase_admin.initialize_app(cred)
# View Starts here

# ONBOARDING API

class OnboardingAPI(APIView): # ???
    
    permission_classes = user_auth_required()
    
    @csrf_exempt
    def get(self, request):
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")
        
        try:
            decoded_token = auth.verify_id_token(token)
            firebase_user_id = decoded_token['user_id']
            main_queryset = User_info.objects.filter(user_firebase_token=firebase_user_id).get()
            main_queryset_serializer = User_info_Serializers(main_queryset)
            if main_queryset_serializer.data['onboarding_status'] == True:
                return Response({"data":"Onboarding Done"},status=status.HTTP_200_OK)
            else:
                return Response({"data":"Onboarding Not Done"},status=status.HTTP_404_NOT_FOUND)
        
        except User_info.DoesNotExist:
            return Response({"data":"User does not exist"},status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(e)
            return Response({"error":"Invalid Token or Token expired"},status=status.HTTP_401_UNAUTHORIZED)
    
    @csrf_exempt
    def post(self, request):
        
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")
        
        try:
            decoded_token = auth.verify_id_token(token)
            firebase_user_id = decoded_token['user_id']
            firebase_user_email = decoded_token['email']
            firebase_user_name = decoded_token['name']
            User_info.objects.get(user_firebase_token=firebase_user_id)
            return Response({"error":"User already exists"},status=status.HTTP_400_BAD_REQUEST)
        
        except User_info.DoesNotExist:
            data = (JSONParser().parse(request))['data']
            main_queryset = User_info.objects.create(user_firebase_token=firebase_user_id)
            User.objects.create_user(email=firebase_user_email,username=firebase_user_name, password=firebase_user_id)
            data_inserted = {"user_prof_type":data['user_prof_type'],
                            "user_meeting_category":data['user_meeting_category'],
                            "email" : firebase_user_email,
                            "onboarding_status": True}
            main_queryset_serializer = User_info_Serializers(main_queryset,data=data_inserted)
            
            if main_queryset_serializer.is_valid():
                main_queryset_serializer.save()
                return Response({"data":main_queryset_serializer.data},status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error":"Invalid Token or Token expired"},status=status.HTTP_401_UNAUTHORIZED)
        
class LandingPageAPI(APIView):
    
    permission_classes = user_auth_required()
    
    @csrf_exempt
    def get(self, request):
        
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")
        
        try:
            decoded_token = auth.verify_id_token(token)
            firebase_user_id = decoded_token['user_id']
            User_info.objects.get(user_firebase_token=firebase_user_id)
                
            # All Meetings
            main_queryset_total_meetings = Summary.objects.filter(user_firebase_token=firebase_user_id)
            main_queryset_summarized = Summary.objects.filter(user_firebase_token=firebase_user_id)
            main_queryset = Summary.objects.filter(user_firebase_token=firebase_user_id).order_by('-meeting_id')[:4][::-1]
            main_queryset_serializer = Summary_Serializers(reversed(main_queryset), many=True)
            
            # Upcoming Meetings
            event_data = Summary.objects.filter(start_time__gte=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ") ,user_firebase_token=firebase_user_id)
            calender_event_serializer_data_upcoming = CalendarEventSerializer(event_data, many=True)
            
            # Past Meetings
            event_data = Summary.objects.filter(start_time__lt=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), user_firebase_token=firebase_user_id)
            calender_event_serializer_data_past = CalendarEventSerializer(event_data, many=True)
            
            return Response({"data":{"meetings":(main_queryset_serializer.data),
                                    "total_meetings":len(main_queryset_total_meetings),
                                    "recent_meetings":(calender_event_serializer_data_past.data),
                                    "scheduled_meetings": (calender_event_serializer_data_upcoming.data),
                                    "summrized_meetings":len(main_queryset_summarized)}
                                },status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error":"Invalid Token or Token expired"},status=status.HTTP_401_UNAUTHORIZED)
    
class AddMeetingAPI(APIView):
    
    permission_classes = user_auth_required()
    
    @csrf_exempt
    def post(self, request):
        
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")
        
        try:
            decoded_token = auth.verify_id_token(token)
            firebase_user_id = decoded_token['user_id']
            User_info.objects.get(user_firebase_token=firebase_user_id)
            
            response_data = JSONParser().parse(request)
            data = response_data.get('data')
            meeting_audio_file_link_new = ""
            main_queryset = User_info.objects.get(user_firebase_token=firebase_user_id)
                        
            Summary.objects.create(user_firebase_token = main_queryset,
                                    title = data.get("meeting_title"),
                                    meet_platform = data.get("meeting_platform"),
                                    meeting_description = data.get("meeting_description"),
                                    attendees_count = data.get("attendees_count"),
                                    start_time = datetime.datetime.strptime(data.get("start_time"), '%Y-%m-%d %H:%M:%S'),
                                    end_time = datetime.datetime.strptime(data.get("end_time"), '%Y-%m-%d %H:%M:%S'),
                                    meeting_location = data.get("meeting_location"),
                                    meeting_transcript = data.get("meeting_transcript"),
                                    is_multilingual = data.get("is_multilingual"),
                                    language = data.get("language"),
                                    meeting_audio_file_link = meeting_audio_file_link_new
                                    )
            
            main_queryset_summary = Summary.objects.filter(user_firebase_token=firebase_user_id).latest('meeting_id')
            main_queryset_summary_serializer = Summary_Serializers(main_queryset_summary)
            
            return Response({"data":
                            {"meeting_data":main_queryset_summary_serializer.data}},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
                print(e)
                return Response({"error":"Invalid Token or Token expired"},status=status.HTTP_401_UNAUTHORIZED)
        
class AddMeetingFileAPI(APIView):
    
    permission_classes = user_auth_required()
    #Swagger Part
    token_param_config = openapi.Parameter('meeting_id', in_= openapi.IN_QUERY, description='meeting_id', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    @csrf_exempt
    def post(self, request, meeting_id):
        
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")
        
        decoded_token = auth.verify_id_token(token)
        firebase_user_id = decoded_token['user_id']
        User_info.objects.get(user_firebase_token=firebase_user_id)
        
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            pathOfFile = file_serializer.data['file']
            newPath = base_path_file + '/' + pathOfFile
            
            main_queryset_summary = Summary.objects.filter(meeting_id=meeting_id, user_firebase_token=firebase_user_id).first()
            main_queryset_summary_serializer = Summary_Serializers(main_queryset_summary)

            # Integfiy platform & detect lang
            meet_platform = identify_meeting_link(main_queryset_summary_serializer.data["meet_link"])
            detected_lang = detect_language(main_queryset_summary_serializer.data["meeting_transcript"])
            
            Summary.objects.filter(meeting_id=meeting_id).update(meeting_audio_file_link=newPath,
                                                                 meet_platform = meet_platform,
                                                                 language = detected_lang,
                                                                 is_summarized=True)
            
            file_extention = newPath.split("/")[-1].split(".")[-1]

            # with open("/Users/cosmos/Desktop/Projects/DeepBlue 2/meeting-summarization-api/data/responses/summary_model_api_response.json", 'rb') as f:
            #     json_data = f.read()
            
            #print(json_data)
            
            # if from_transcript file type then send to
            if file_extention in TRANCRIPT_EXT:
                print("\n TRANCRIPT DETECTED")
                meeting_type = 'from_transcript'
            
                # preprocess it and add new data using preprocessor function {Expecting the files in our format}
                
                segmented_df,speaker_dialogue,durations,attendeces_count = any_transcript_to_dataframe(newPath)
                segmented_df_2 = start_end_from_transcript(segmented_df,file_extension = newPath.split(".")[-1])
                response_json = dict({'data':{"transcript":speaker_dialogue,"segmented_df": json.loads(segmented_df_2.to_json(orient='records'))}})
                print(response_json)
                # response_json={'transcript': "Claire: Hi everyone, welcome to our weekly team meeting.\nMark: Hi Claire, thanks for having us.\nClaire: Today we'll be discussing the progress on the new project.\nEmma: I have some updates on the project. The design work is almost done.\nJohn: Great to hear that Emma, what about the development work?"}
                #--> send to summarization
                try:
                    response = requests.post(url = URL_MICRO + "summarization", data=json.dumps(response_json))
                    response.raise_for_status()
                    response.raise_for_status()
                    models_data = (response.json())['data']
                    # models_data = (json.loads(response.json()))['data']
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    print("Down")
                except requests.exceptions.HTTPError:
                    print("4xx, 5xx")
                
                #models_data = (json.loads(json_data))['data']
                
                try:
                    top_time_spent_person = models_data.get('metadata')['top_speaker'][0]
                except KeyError:
                    top_time_spent_person = ""
                    
                #save data
                Summary.objects.filter(meeting_id=meeting_id).update(meeting_duration = durations,
                                                                     is_summarized = True,
                                                                     meeting_type = meeting_type,
                                                                     attendees_count = attendeces_count,
                                                                     summary_gen_date = datetime.datetime.now(),
                                                                     meeting_summary = models_data['summary'],
                                                                     sentiments = ''.join(models_data['extras']['sentiments']),
                                                                     decisions = ','.join(models_data['extras']['decisions']),
                                                                     action_items = ','.join(set(models_data['extras']['action_items'] + models_data['metadata']['action_items'])),
                                                                    #  top_speaker = ','.join(models_data.get('metadata').get('top_speaker'),
                                                                     meeting_description = models_data['metadata']['meeting_description'],
                                                                     generated_title = models_data['metadata']['generated_title'],
                                                                     topic = models_data['metadata']['meeting_category_assgined'],
                                                                     roles_detected = json.dumps(models_data['metadata']['roles_detected']),
                                                                     top_spent_time_person = top_time_spent_person,
                                                                     reading_time = len(models_data['summary'].split(" "))/200,
                                                                     speaker_json = json.dumps({"sepakers":models_data['metadata']['speaker_final']}),
                                                                     model_used = models_data['models_used'],
                                                                     highlights_json = json.dumps(models_data['highlights']),
                                                                     transcript_json = json.dumps(models_data['transcript']),
                                                                     )
                                
                
            if file_extention in VIDEO_EXT:
                # if from_video_audio
                #--> send to trancription & get the trancript +
                print("\n VIDEO FILE DETECTED \n")
                meeting_type = 'from_video_audio'
                with open(newPath, 'rb') as f:
                    try:
                        response = requests.post(URL_MICRO + "transcript" , files={'file': f})
                        response.raise_for_status()
                        transcript_data = json.loads(response.json())
                    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                        print("Down")
                    except requests.exceptions.HTTPError:
                        print("4xx, 5xx")
                        
                        
                # preprocess it and add new data using preprocessor function
                #--> send to summarization
                try:
                    response = requests.post(URL_MICRO + "summarization" ,data=json.dumps(transcript_data['transcript']))
                    response.raise_for_status()
                    transcript_from_res = json.loads(response.json())
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    print("Down")
                except requests.exceptions.HTTPError:
                    print("4xx, 5xx")
                
                #save data
                Summary.objects.filter(meeting_id=meeting_id).update(meeting_duration = durations,
                                                                     is_summarized = True,
                                                                     meeting_type = meeting_type,
                                                                     attendees_count = attendeces_count,
                                                                     summary_gen_date = datetime.datetime.now(),
                                                                     meeting_summary = models_data['summary'],
                                                                     sentiments = ','.join(models_data['extras']['sentiments']),
                                                                     decisions = ','.join(models_data['extras']['decisions']),
                                                                     action_items = ','.join(set(models_data['extras']['action_items'] + models_data['metadata']['action_items'])),
                                                                     top_speaker = ','.join(models_data['metadata']['top_speaker']),
                                                                     meeting_description = models_data['metadata']['meeting_description'],
                                                                     generated_title = models_data['metadata']['generated_title'],
                                                                     topic = models_data['metadata']['meeting_category_assgined'],
                                                                     roles_detected = json.dumps(models_data['metadata']['roles_detected']),
                                                                     top_spent_time_person = top_time_spent_person,
                                                                     reading_time = len(models_data['summary'].split(" "))/200,
                                                                     speaker_json = json.dumps({"sepakers":models_data['metadata']['speaker_final']}),
                                                                     model_used = models_data['model_used'],
                                                                     )
            
        return Response({"data":{"meeting_id":meeting_id,"status":"File uploaded successfully"}},status=status.HTTP_201_CREATED)  # ADD A REDIRECT URL HERE

class SummaryPageAPI(APIView):
    
    permission_classes = user_auth_required()
    
    def get(self, request, meeting_id):
        
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")

        decoded_token = auth.verify_id_token(token)
        firebase_user_id = decoded_token['user_id']
        User_info.objects.get(user_firebase_token=firebase_user_id)

        data_dict = {}
        meta_data_dict={}
        meta_data_list=[]
        meeting_data_dict = {}
        meeting_data_list = []
        summary_dict = {}
        summary_data_list =[]
        try:
            main_queryset = Summary.objects.get(meeting_id=meeting_id)
        except ObjectDoesNotExist:
            return Response({"data":{"error":"Meeting Summary does not exist"}},status=status.HTTP_400_BAD_REQUEST)
        summary_serializer = Summary_Serializers(main_queryset)
        content = summary_serializer.data
        data_dict['meeting_type'] = content.get("meeting_type")
        data_dict['meeting_id']  = content.get("meeting_id")
        data_dict['is_summarized'] = content.get("is_summarized")

        data_dict["transcript"] = [content.get("meeting_transcript")]

        for single_key in listofkeys:
            meta_data_dict[single_key] = content.get(single_key)
        try:
            meta_data_dict['speaker'] =  json.loads(content.get('speaker_json')).get('sepakers')
        except :
            meta_data_dict['speaker']=[]
        meta_data_list.append(meta_data_dict)
        meeting_data_dict["metadata"] = meta_data_list

        for single_key in summary_dict_key:
            summary_dict[single_key] = content.get(single_key)
        summary_dict['agenda'] = ['General Meeting','Disccusion']
        try:
            summary_dict['highlights'] = json.loads(content.get('highlights_json')) #[" "]   #om will do
        except:
            summary_dict['highlights']=[]
        summary_data_list.append(summary_dict)
        meeting_data_dict['summary'] = summary_data_list
        try:
            meeting_data_dict['trascript'] = json.loads(str(content.get('transcript_json')))
        except Exception as e:
            print(e, "\nerror in transcript json\n")
            meeting_data_dict['trascript'] = []
        meeting_data_list.append(meeting_data_dict)
        data_dict['meeting_data'] = meeting_data_list
        data_dict["email_redirect"] = f"mailto:{decoded_token['email']}"

        return Response({"data":data_dict},status=status.HTTP_200_OK)
    
    def post(self,request,meeting_id):
        try :
                    
            authorization_header = request.META.get('HTTP_AUTHORIZATION')
            token = authorization_header.replace("Bearer ", "")
            
            decoded_token = auth.verify_id_token(token)
            firebase_user_id = decoded_token['user_id']
            User_info.objects.get(user_firebase_token=firebase_user_id)
            
            response_data = request.body.decode('utf-8')
            query_set = Summary.objects.get(meeting_id=meeting_id)
            main_queryset_serializer = Summary_Serializers(query_set)
            content = main_queryset_serializer.data

            #retrieving the old transcript
            if not (content.get('is_summary_edited')):
                query_set.meeting_old_summary = content.get('meeting_summary')
                query_set.is_summary_edited = True
                
            #saving user edited transcript
            query_set.meeting_summary =  preprocess_hocr(response_data)
            query_set.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e :
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
   
class StartSummarization(APIView):
    
    permission_classes = user_auth_required()
    
    def get(self, request, meeting_id):
        try:
            main_queryset = Summary.objects.get(meeting_id=meeting_id)
            main_queryset_serializer = Summary_Serializers(main_queryset)
            
        except ObjectDoesNotExist:
            return Response({"data":{"error":"Meeting Summary does not exist"}},status=status.HTTP_400_BAD_REQUEST)
        import time
        time.sleep(10)
        # Start summarization ------------------------------------------------>
        
        Summary.objects.filter(meeting_id=meeting_id).update(is_summarized = True)
        return Response({"data":{"meeting_id":meeting_id,"status":"Summarization started"}},status=status.HTTP_200_OK)
    
class DownloadpdfAPI(APIView):
    
    permission_classes = user_auth_required()
    
    def get(self,request,meeting_id):
        
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")
        
        decoded_token = auth.verify_id_token(token)
        firebase_user_id = decoded_token['user_id']
        User_info.objects.get(user_firebase_token=firebase_user_id)
        
        main_queryset = Summary.objects.filter(meeting_id=meeting_id)
        main_queryset_serializer = Summary_Serializers(main_queryset,many=True)
        content = main_queryset_serializer.data
        path = os.path.join(base_path_file,"media",f'{meeting_id}.pdf')
        txt_to_pdf(content[0]['meeting_summary'],path)
        return Response({"data":{"path" : path}},status=status.HTTP_200_OK)
        

class EditUserDataAPI(APIView) :
    
    permission_classes = user_auth_required()
    
    def get(self,request):
        
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")
        
        decoded_token = auth.verify_id_token(token)
        firebase_user_id = decoded_token['user_id']
        User_info.objects.get(user_firebase_token=firebase_user_id)
        
        User_data = User_info.objects.get(user_firebase_token=firebase_user_id)
        User_data_serializer = User_info_Serializers(User_data)
        return Response({"data": {"user_data": 
                            {"name": User_data_serializer.data['name'],
                             "username": User_data_serializer.data['username'],
                             "email": User_data_serializer.data['email'],
                             "user_prof_type": User_data_serializer.data['user_prof_type'],
                             "user_meeting_category": User_data_serializer.data['user_meeting_category'].split(",")},
                             "calender_onboarding_status": User_data_serializer.data['calender_onboarding_status'],
                        }}, status=status.HTTP_200_OK)

    @csrf_exempt
    def post(self,request):
        try :
            
            authorization_header = request.META.get('HTTP_AUTHORIZATION')
            token = authorization_header.replace("Bearer ", "")
            
            decoded_token = auth.verify_id_token(token)
            firebase_user_id = decoded_token['user_id']
            User_info.objects.get(user_firebase_token=firebase_user_id)

            #getting the data from the request
            data = JSONParser().parse(request)['data']['user_data']
            User_info.objects.filter(user_firebase_token = firebase_user_id).update(
                name = data['name'],
                username = data['username'],
                user_prof_type = data['user_prof_type'],
                user_meeting_category = data['user_meeting_category'],
            )
            return Response(status=status.HTTP_200_OK)
        except Exception as e :
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
# FEEEDBACK API

class FeedBackAPI(APIView) :
    
    permission_classes = user_auth_required()
    
    def get(self,request,meeting_id,param,val):
        
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")
        decoded_token = auth.verify_id_token(token)
        firebase_user_id = decoded_token['user_id']
        User_info.objects.get(user_firebase_token=firebase_user_id)
        
        if param == "factual_consistency":
            if val == 0:
                Summary.objects.filter(meeting_id=meeting_id).update(factual_consistency=0)
            else :
                Summary.objects.filter(meeting_id=meeting_id).update(factual_consistency=1)
        if param == "is_good":
            if val == 2:
                Summary.objects.filter(meeting_id=meeting_id).update(is_good=2)
            else:
                Summary.objects.filter(meeting_id=meeting_id).update(is_good=0)
            
        return Response({"status": "updated"},status=status.HTTP_200_OK)
    
# ANALYTICS API

class AnalyticsAPI(APIView) : # ??
    
    permission_classes = user_auth_required()
    
    def get(self,request,user_id):
        
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")
        decoded_token = auth.verify_id_token(token)
        firebase_user_id = decoded_token['user_id']
        User_info.objects.get(user_firebase_token=firebase_user_id)
        
        main_queryset = Summary.objects.filter(meeting_id=user_id)
        main_queryset_serializer = Summary_Serializers(main_queryset,many=True)
        content = main_queryset_serializer.data
        return Response({"data": {"analytics_data": content}}, status=status.HTTP_200_OK)

class ChatbotAPI(APIView) :
    
    permission_classes = user_auth_required()
    
    def get(self,request,summary,meeting_id):
        
        if summary == "summary":
            main_queryset = Summary.objects.filter(meeting_id=meeting_id)
            main_queryset_serializer = Summary_Serializers(main_queryset,many=True)
            content = main_queryset_serializer.data
            return Response({"data": {"chatbot_data": content}}, status=status.HTTP_200_OK)