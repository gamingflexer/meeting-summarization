from views.models import ModelSelect

def ModelSelectFromLength(transcript):
    words = transcript.split(" ")
    if len(words) < 100:
        print("\n Short & Very Short Meeting  \n")

        """ vmarklynn/bart-large-cnn-icsi-ami-v3 """
        model_used = "vmarklynn/bart-large-cnn-icsi-ami-v3"
        new_model = ModelSelect(modelname = 'bart',model_id_or_path = model_used ,text = transcript,max_new_tokens=200)
        model = new_model.load_model()
        results = new_model.generate_summary(model)
        return results,model_used

    elif len(words) < 350:
        print("\n Medium Meeting \n")

        """ vmarklynn/bart-large-cnn-icsi-ami-v3 """
        model_used = "vmarklynn/bart-large-cnn-icsi-ami-v3"
        new_model = ModelSelect(modelname = 'bart',model_id_or_path = model_used, text = transcript,max_new_tokens=200)
        model = new_model.load_model()
        results = new_model.generate_summary(model)
        return results,model_used

    elif len(words) < 500:
        print("\n Long Meeting \n")

        """
        vmarklynn/bart-large-cnn-samsum-icsi-ami
        asach/led-samsum-kunal
        """

        model_used_1 = "vmarklynn/bart-large-cnn-samsum-icsi-ami"
        model_used_2 = "asach/led-samsum-kunal"

        new_model_1 = ModelSelect(modelname = 'bart',model_id_or_path= model_used_1,text = transcript,max_new_tokens=200)
        model_1 = new_model_1.load_model()
        results_1 = new_model_1.generate_summary(model_1)
        
        new_model_2 = ModelSelect(modelname = 'longformer',model_id_or_path= model_used_2,text = transcript,max_new_tokens=200)
        model_2 = new_model_2.load_model()
        results_2 = new_model_2.generate_summary(model_2)

        results_concat = str(results_1) + str(results_2)
        models_conact = str(model_used_1 + ',' + model_used_2)

        return results_concat,models_conact


    elif len(words) > 500 and len(words) < 1200:
        print("\n Very Long Meeting \n")

        """ 
        mikeadimech/longformer-qmsum-meeting-summarization 
        asach/lognt5-xsum-icsi-400-10 [Important points from second line]
        """

        model_used_1 = "mikeadimech/longformer-qmsum-meeting-summarization"
        model_used_2 = "asach/lognt5-xsum-icsi-400-10"

        new_model_1 = ModelSelect(modelname = 'longformer',model_id_or_path= model_used_1,text = transcript,max_new_tokens=200)
        model_1 = new_model_1.load_model()
        results_1 = new_model_1.generate_summary(model_1)
        
        new_model_2 = ModelSelect(modelname = 'longt5',model_id_or_path= model_used_2,text = transcript,max_new_tokens=200)
        model_2 = new_model_2.load_model()
        results_2 = new_model_2.generate_summary(model_2)
        results_2_edited = ".".join(results_2.split(".")[:1])

        results_concat = str(results_1) + str(results_2)
        models_conact = str(model_used_1 + ',' + model_used_2)

        return results_concat,models_conact

    elif len(words) > 1200 and len(words) < 5000:
        print("\n Extreme Long Meeting\n")

        """
        MingZhong/DialogLED-base-16384 [Overview with imp points]
        asach/lognt5-xsum-icsi-400-10 [Important points from second line]
        """

        model_used_1 = "asach/DialogLED-yash-samsum"
        model_used_2 = "asach/lognt5-xsum-icsi-400-10"

        new_model_1 = ModelSelect(modelname = 'led',model_id_or_path= model_used_1,text = transcript,max_new_tokens=200)
        model_1 = new_model_1.load_model()
        results_1 = new_model_1.generate_summary(model_1)
        
        new_model_2 = ModelSelect(modelname = 'longt5',model_id_or_path= model_used_2,text = transcript,max_new_tokens=200)
        model_2 = new_model_2.load_model()
        results_2 = new_model_2.generate_summary(model_2)
        results_2_edited = ".".join(results_2.split(".")[:1])

        results_concat = str(results_1) + str(results_2)
        models_conact = str(model_used_1 + ',' + model_used_2)

        return results_concat,models_conact
    
    else:
        print("\n SEGMENTED | Extreme Long Meeting\n")

        """
        MingZhong/DialogLED-base-16384 [Overview with imp points]
        asach/lognt5-xsum-icsi-400-10 [Important points from second line]
        """
        split_point = len(transcript) // 2

        transcript_part_1 = transcript[:split_point]
        transcript_part_2 = transcript[split_point:]

        model_used_1 = "asach/DialogLED-yash-samsum"
        

        new_model_1 = ModelSelect(modelname = 'led',model_id_or_path= model_used_1,text = transcript_part_1,max_new_tokens=200)
        model_1 = new_model_1.load_model()
        results_1 = new_model_1.generate_summary(model_1)
        
        new_model_1 = ModelSelect(modelname = 'led',model_id_or_path= model_used_1,text = transcript_part_2,max_new_tokens=200)
        model_1 = new_model_1.load_model()
        results_2 = new_model_1.generate_summary(model_1)

        results_concat = str(results_1 + '.' + results_2)
        models_conact = str(model_used_1)

        return results_concat,models_conact
    
