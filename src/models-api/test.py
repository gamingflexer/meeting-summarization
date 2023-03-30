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
# tokenizer = AutoTokenizer.from_pretrained("asach/lognt5-xsum-icsi-400-10")
# model = LongT5ForConditionalGeneration.from_pretrained("asach/lognt5-xsum-icsi-400-10").to("cuda").half()
# tokenizer = AutoTokenizer.from_pretrained("asach/lognt5-xsum-icsi-5")
# model = LongT5ForConditionalGeneration.from_pretrained("asach/lognt5-xsum-icsi-5").to("cuda").half()
# tokenizer = AutoTokenizer.from_pretrained("asach/led-dialogSum-1epoch")
# model = LEDForConditionalGeneration.from_pretrained("asach/led-dialogSum-1epoch").to("cuda").half()
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("microsoft/GODEL-v1_1-large-seq2seq")
model = AutoModelForSeq2SeqLM.from_pretrained("microsoft/GODEL-v1_1-large-seq2seq")