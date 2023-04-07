from views.models import ModelSelect

data = {
    "bart": [
        {
            "model_id": "asach/bart-highlights-redit",
            "path": "asach/bart-highlights-redit",
            "dataset": "samsum",
            "perfomance": 0,
            "topics": [],
            "notes": "",
            "type": ""
        }
    ]
}

for model_name in data:
    for model in data[model_name]:
        newmodel = ModelSelect(modelname = model_name,text = "dd",
                            model_id_or_path = model['model_id'],max_new_tokens = 200)
        model = newmodel.load_model()
        del model

import torch
from transformers import AutoTokenizer, AutoModel, LongT5ForConditionalGeneration, LEDForConditionalGeneration

# load tokenizer
tokenizer = AutoTokenizer.from_pretrained("asach/lognt5-xsum-icsi-400-10")
model = LongT5ForConditionalGeneration.from_pretrained("asach/lognt5-xsum-icsi-400-10").to("cuda").half()
tokenizer = AutoTokenizer.from_pretrained("asach/lognt5-xsum-icsi-5")
model = LongT5ForConditionalGeneration.from_pretrained("asach/lognt5-xsum-icsi-5").to("cuda").half()
tokenizer = AutoTokenizer.from_pretrained("asach/led-dialogSum-1epoch")
model = LEDForConditionalGeneration.from_pretrained("asach/led-dialogSum-1epoch").to("cuda").half()
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def processors_call_on_trancript(transcript): # in the format of the json | whisper
    transcript_joined = ""
    for segment in transcript:
        transcript_joined += segment['text'] # no speaker info
            
    # non-formatted transcript preprocessor
    trancript_object = PreProcesssor(transcript_joined)
    email,date,phone_numbers,addresses = trancript_object.get_entites()
    speaker_names = trancript_object.get_speaker_names()
    corrected_text = trancript_object.get_corrected_text()
    jargon_sentences = trancript_object.get_jargon_sentences()
    action_items_list = trancript_object.get_action_items()
    
    # formatted transcript preprocessor
    
    #Convert to DataFrame
    df = pd.DataFrame(transcript) ########## this is the transcript
    
    trancript_prepocessor_object = TranscriptPreProcessor()
    analyse_transcript_var = trancript_prepocessor_object.analyse_transcript(df)
    get_interactions_silence = trancript_prepocessor_object.get_interactions_silence(df)
    backchannels = trancript_prepocessor_object.get_backchannels(df)
    stats = trancript_prepocessor_object.get_stats(df)
    df_cluster = trancript_prepocessor_object.get_cluster(df) # what to do with this?
    
    new_model = ModelSelect(modelname = 'bart',model_id_or_path= 'knkarthick/MEETING_SUMMARY',text = transcript,max_new_tokens=200)
    model = new_model.load_model()
    summary_main = new_model.generate_summary(model)
    
    # postprocessor on the summary
    summary_main_object = PostProcesssor(summary_main)
    clean_summary = summary_main_object.get_clean_summary()
    formatted_summary = summary_main_object.get_formatted_summary(clean_summary)
    
    return {"summary": formatted_summary, 
            "meta_data":{"email":email,
                        "imp_dates":date,
                        "phone_numbers":phone_numbers,
                        "human_names":speaker_names,
                        "addresses":addresses,
                        "jargon_sentences":jargon_sentences,
                        "action_items":action_items_list,
                        "analyse_transcript":analyse_transcript_var,
                        "get_interactions_silence":get_interactions_silence,
                        "backchannels":backchannels,
                        "stats":stats,
                        "df_cluster":df_cluster}}
                         
tokenizer = AutoTokenizer.from_pretrained("microsoft/GODEL-v1_1-large-seq2seq")
model = AutoModelForSeq2SeqLM.from_pretrained("microsoft/GODEL-v1_1-large-seq2seq")