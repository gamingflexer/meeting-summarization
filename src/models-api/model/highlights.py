from views.models import ModelSelect
from transformers import AutoTokenizer
import nltk
import math

def get_highlights(df):

    """ ADD internal_timestamps """

    n_rows = len(df)
    start_rows = math.ceil(n_rows * 0.25)
    main_rows = n_rows - start_rows * 2
    end_rows = start_rows

    # Create a list of segment names with the appropriate number of rows
    segments = ['start'] * start_rows + ['main_context'] * main_rows + ['end'] * end_rows

    # Add the "main_timestamps" column to the DataFrame with the segment names
    df['main_timestamps'] = segments

    # Calculate the number of internal headline rows for each main context segment
    internal_headline_rows = math.ceil(main_rows / 2)

    # Initialize the counter for the internal headline row number
    internal_headline_counter = 1

    # Add the "internal_headlines" column to the DataFrame with the appropriate values
    internal_headlines = []
    start_counter = 1
    end_counter = 1


    for segment in segments:
        if segment == 'start':
            internal_headlines.append(segment + f'_{start_counter}')
            start_counter += 1
        elif segment == 'end':
            internal_headlines.append(segment + f'_{end_counter}')
            end_counter += 1
        else:
            if internal_headline_counter <= internal_headline_rows:
                internal_headlines.append('main_' + str(internal_headline_counter))
            else:
                internal_headlines.append('main_' + str(internal_headline_counter))
            internal_headline_counter += 1
    df['internal_timestamp'] = internal_headlines

    """ ADD main_headlines & internal_headlines """

    df['main_headlines'] = df['main_timestamps'].apply(lambda x: (x.split('_')[0]) + '_headline')
    df['internal_headlines'] = df['internal_timestamp'].apply(lambda x: x + '_headline')
    try:
        df.drop(columns=['page_number'],inplace=True)
    except:
        pass

        #get the rows where "main_timestamps" is start
    start_sentences = segmented_df[segmented_df['main_timestamps'] == 'start']
    main_context_sentences = segmented_df[segmented_df['main_timestamps'] == 'main_context']
    end_sentences = segmented_df[segmented_df['main_timestamps'] == 'end']

    start_joined = " ".join(start_sentences['text'].to_list())
    main_context_joined = " ".join(main_context_sentences['text'].to_list())
    end_joined = " ".join(end_sentences['text'].to_list())

    # get the rows where " .. " is start

    # 1
    start_sentences_internal_1 = start_sentences[start_sentences['internal_timestamp'] == 'start_1']
    main_context_sentences_internal_1 = main_context_sentences[main_context_sentences['internal_timestamp'] == 'main_1']
    end_sentences_internal_1 = end_sentences[end_sentences['internal_timestamp'] == 'end_1']

    start_joined_internal_1 = " ".join(start_sentences_internal_1['text'].to_list())
    main_context_joined_internal_1 = " ".join(main_context_sentences_internal_1['text'].to_list())
    end_joined_internal_1 = " ".join(end_sentences_internal_1['text'].to_list())

    # 2
    start_sentences_internal_2 = start_sentences[start_sentences['internal_timestamp'] == 'start_2']
    main_context_sentences_internal_2 = main_context_sentences[main_context_sentences['internal_timestamp'] == 'main_2']
    end_sentences_internal_2 = end_sentences[end_sentences['internal_timestamp'] == 'end_2']

    start_joined_internal_2 = " ".join(start_sentences_internal_2['text'].to_list())
    main_context_joined_internal_2 = " ".join(main_context_sentences_internal_2['text'].to_list())
    end_joined_internal_2 = " ".join(end_sentences_internal_2['text'].to_list())

    title_model = ModelSelect(modelname = "title",model_id_or_path = "fabiochiu/t5-small-medium-title-generation", max_new_tokens=100, text=" ")
    title_model_model = title_model.load_model()

    def title_inside_df(segmented_df,timestamp,headline,text):
        inputs = ["summarize: " + text]
        tokenizer = AutoTokenizer.from_pretrained("fabiochiu/t5-small-medium-title-generation")
        inputs = tokenizer(inputs, truncation=True, return_tensors="pt").to("cuda")
        output = title_model_model.generate(**inputs, num_beams=4, do_sample=True, min_length=5, max_length=10)
        decoded_output = tokenizer.batch_decode(output, skip_special_tokens=True)[0]
        predicted_title = nltk.sent_tokenize(decoded_output.strip())[0]
        segmented_df[headline] = segmented_df[headline].replace(timestamp,predicted_title)

    title_inside_df(segmented_df,'start_headline','main_headlines',start_joined)
    title_inside_df(segmented_df,'main_headline','main_headlines',main_context_joined)
    title_inside_df(segmented_df,'end_1_headline','main_headlines',end_joined)

    title_inside_df(segmented_df,'start_1_headline','internal_headlines',start_joined_internal_1)
    title_inside_df(segmented_df,'main_1_headline','internal_headlines',main_context_joined_internal_1)
    title_inside_df(segmented_df,'end_headline','internal_headlines',end_joined_internal_1)

    title_inside_df(segmented_df,'start_2_headline','internal_headlines',start_joined_internal_2)
    title_inside_df(segmented_df,'main_2_headline','internal_headlines',main_context_joined_internal_2)
    title_inside_df(segmented_df,'end_2_headline','internal_headlines',end_joined_internal_2)


    """ CONVERT TO OUR FORMAT """

    try:
        df['start_time'] = pd.to_datetime(df['start_time'], unit='s').dt.time.apply(lambda x: x.strftime('%H:%M:%S'))
        df['internal_time'] = pd.to_datetime(df['duration'], unit='s').dt.time.apply(lambda x: x.strftime('%H:%M:%S'))
        df['main_timestamp'] = pd.to_datetime(df['main_timestamp'], unit='s').dt.time.apply(lambda x: x.strftime('%H:%M:%S'))
    except:
        pass

    # Group the rows by the main_timestamps column and create a nested dictionary
    output_dict = {
        'main_timestamps': []
    }

    for group_name, group_data in df.groupby('main_timestamps'):
        main_timestamp_dict = {
            'timestamp': str(group_data['main_timestamps'].iloc[0]),
            'headline': group_data['main_headlines'].iloc[0],
            'internal_timestamp': []
        }
        for i, row in group_data.iterrows():
            internal_timestamp_dict = {
                'time': row['start_time'],
                'text': row['internal_headlines']
            }
            main_timestamp_dict['internal_timestamp'].append(internal_timestamp_dict)

        output_dict['main_timestamps'].append(main_timestamp_dict)

    return [output_dict],df