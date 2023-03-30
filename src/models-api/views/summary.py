from views.models import ModelSelect

def ModelSelectFromLength(transcript):
    words = transcript.split(" ")
    if len(words) < 100:
        print("\n Short & Very Short Meeting  \n")

        """ vmarklynn/bart-large-cnn-icsi-ami-v3 """

        new_model = ModelSelect(modelname = 'bart',model_id_or_path= 'vmarklynn/bart-large-cnn-icsi-ami-v',text = transcript,max_new_tokens=200)
        model = new_model.load_model()
        results = new_model.generate_summary(model)
        return results

    elif len(words) < 350:
        print("\n Medium Meeting \n")

        """ vmarklynn/bart-large-cnn-icsi-ami-v3 """

        new_model = ModelSelect(modelname = 'bart',model_id_or_path= 'vmarklynn/bart-large-cnn-icsi-ami-v',text = transcript,max_new_tokens=200)
        model = new_model.load_model()
        results = new_model.generate_summary(model)
        return results

    elif len(words) < 500:
        print("\n Long Meeting \n")

        """
        vmarklynn/bart-large-cnn-samsum-icsi-ami
        asach/led-samsum-kunal
        """
        new_model_1 = ModelSelect(modelname = 'bart',model_id_or_path= 'vmarklynn/bart-large-cnn-samsum-icsi-ami',text = transcript,max_new_tokens=200)
        model_1 = new_model_1.load_model()
        results_1 = new_model_1.generate_summary(model)
        
        new_model_2 = ModelSelect(modelname = 'longformer',model_id_or_path= '',text = transcript,max_new_tokens=200)
        model_2 = new_model_2.load_model()
        results_2 = new_model_2.generate_summary(model)

        return str(results_1) + str(results_2)


    elif len(words) > 500 and len(words) < 1200:
        print("\n Very Long Meeting \n")

        """ 
        mikeadimech/longformer-qmsum-meeting-summarization 
        asach/lognt5-xsum-icsi-400-10 [Important points from second line]
        """
        new_model_1 = ModelSelect(modelname = 'longformer',model_id_or_path= 'mikeadimech/longformer-qmsum-meeting-summarization ',text = transcript,max_new_tokens=200)
        model_1 = new_model_1.load_model()
        results_1 = new_model_1.generate_summary(model)
        
        new_model_2 = ModelSelect(modelname = 'longt5',model_id_or_path= 'asach/lognt5-xsum-icsi-400-10',text = transcript,max_new_tokens=200)
        model_2 = new_model_2.load_model()
        results_2 = new_model_2.generate_summary(model)
        results_2_edited = (results_2.split(".")[:1]).join(".")
        return str(results_1) + str(results_2_edited)

    else: 
        print("\n Extreme Long Meeting\n")

        """
        MingZhong/DialogLED-base-16384 [Overview with imp points]
        asach/lognt5-xsum-icsi-400-10 [Important points from second line]
        """
        new_model_1 = ModelSelect(modelname = 'led',model_id_or_path= 'MingZhong/DialogLED-base-16384',text = transcript,max_new_tokens=200)
        model_1 = new_model_1.load_model()
        results_1 = new_model_1.generate_summary(model)
        
        new_model_2 = ModelSelect(modelname = 'longt5',model_id_or_path= 'asach/lognt5-xsum-icsi-400-10',text = transcript,max_new_tokens=200)
        model_2 = new_model_2.load_model()
        results_2 = new_model_2.generate_summary(model)
        results_2_edited = (results_2.split(".")[:1]).join(".")
        return str(results_1) + str(results_2_edited)
    
