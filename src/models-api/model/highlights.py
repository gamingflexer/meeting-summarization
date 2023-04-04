from models import bart_title_summarizer
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
    df.drop(columns=['page_number'],inplace=True)

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

    return [output_dict]