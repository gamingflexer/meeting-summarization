from views.models import ModelSelect

data = {
    "longformer": [
        {
            "model_id": "MingZhong/DialogLED-base-16384",
            "path": "MingZhong/DialogLED-base-16384",
            "dataset": "DialogSum",
            "perfomance": 0,
            "topics": [],
            "notes": "large model",
            "type": "Abstractive"
        }
    ],
    "pegasus": [
        {
            "model_id": "google/pegasus-xsum",
            "path": "hobab185/pegasus-pn_summary",
            "dataset": "",
            "perfomance": 0,
            "topics": [],
            "notes": "",
            "type": ""
        }
    ],
    "bart": [
        {
            "model_id": "knkarthick/meeting-summary-samsum",
            "path": "knkarthick/meeting-summary-samsum",
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
        newmodel = ModelSelect(modelname = model_name,
                            model_id_or_path = model['model_id'])
        model = newmodel.load_model()
        del model

