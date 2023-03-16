from views.models import ModelSelect

data = {
    "bart": [
        {
            "model_id": "knkarthick/MEETING_SUMMARY",
            "path": "knkarthick/MEETING_SUMMARY",
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

