print("\n Loading Sub Modules ... \n")
from converse.pyconverse import Callyzer, SpeakerStats
from converse.pyconverse.segmentation import SemanticTextSegmentation
from converse.pyconverse.zeroshot_topic_model import  ZeroShotTopicFinder
print("\n Done \n")
from preprocessing import get_clusters

import pandas as pd
import spacy
import nltk
spacy.load('en_core_web_sm')

class TranscriptPreProcessor():
    
    def __init__(self, transcript, # trancript is a df file here
                 backchannels,
                 column_utter = 'utterance',
                 column_speaker = 'speaker',
                 column_start_time = 'start_time',
                 column_end_time = 'end_time'):
        
        self.zst = ZeroShotTopicFinder()
        self.transcript = transcript #json
        self.df = pd.DataFrame(self.transcript)
        
        """
        Columns: speaker | start_time | end_time | utterance/text
        """
        
        self.column_utter = column_utter
        self.column_speaker = column_speaker
        self.column_start_time = column_start_time
        self.column_end_time = column_end_time
        
        # Other variables
        self.backchannels = backchannels #Can be "nlp" or "keyword"
        
    def analyse_transcript(self):
        transcript_analysis = Callyzer(data=self.df, 
                                       utterance=self.column_utter, 
                                       speaker=self.column_speaker, 
                                       starttime=self.column_start_time, 
                                       endtime=self.column_end_time)
        return transcript_analysis
        
    def get_interactions_silence(self,transcript_analysis):
        """INTERACTIONS"""
        
        interruptions = transcript_analysis.get_interruption() #interruption periods in a call
        silence = transcript_analysis.get_silence() #periods of silence in a call
        
        return interruptions, silence
        
    def get_backchannels(self,transcript_analysis):
        """MARK THE Keywords as Backchannels True/False""" #  like 'hmm' or 'uh-huh' ['is_backchannel]
        
        if self.backchannels == "keyword": # both are dataframe
            backchannels_via_keywords = transcript_analysis.tag_backchannel().query("is_backchannel == True") #identify backchannel utterances via keywords
            return backchannels_via_keywords
        else:
            backchannels_via_transformers = transcript_analysis.tag_backchannel(type='nlp').query("is_backchannel == True") #identify backchannel utterances with sentence-transformers
            return backchannels_via_transformers
        
            
    def get_emotions(self,transcript_analysis):
        """Get Questions and Answers""" # ['is_question']
        
        questions = transcript_analysis.tag_questions().query("is_question == True") #identiy utterances which are questions ['is_question']
        
        """GET EMOTIONS & EMPAHTIC WORDS""" # ['is_empathy'] ['emotion']
        
        emotions = transcript_analysis.tag_emotion(); emotions[["speaker", "utterance", "emotion"]]
        empathy = transcript_analysis.tag_empathy(); empathy[["speaker", "utterance", "is_empathy"]]

        return questions, emotions, empathy
    
    def get_speaker_stats(self):
        """Get Speaker Stats"""
        
        stats = SpeakerStats(self.df, speaker='speaker').get_stats()
        
        return stats
    
    def get_segments(self):
        """GET SEGMENTS"""   
        
        df_grouped = self.df.groupby('speaker')['utterance'].apply(lambda x: ' '.join(x)).reset_index()
        df_grouped['speaker_dialogue'] = df_grouped['speaker'] + ': ' + df_grouped['utterance']
        speaker_dialogue = df_grouped['speaker_dialogue'].str.cat(sep=' ')  # concatenate all the speaker dialogue
             
        #Get Topic for each segment
        
        clusters = get_clusters(self.transcript)
        
        # convert clusters to dataframe for semantic segmentation
        # Segments
        segments = SemanticTextSegmentation(self.df).get_segments()
        
        topics = []
        clusters = {}
        text_pairs = []
        for text_pairs in segments:
            clusters.update({segments.index(text_pairs):{"segments":text_pairs,"topics":self.zst.find_topic(text_pairs)}})
    
        df_cluster = pd.DataFrame(clusters)
        
        #get Title for the segments 
        
        return df_cluster