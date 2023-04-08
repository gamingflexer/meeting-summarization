# -*- coding: utf-8 -*-
"""Separation_text.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1B0lQ68IFpT5kjPUoazCXdagSTnbhV8eS
"""

! pip install tabula-py

import pandas as pd
import numpy as np
import tabula
import math

def calculate_duration(sentence):
      num_words = len(sentence.split())
      duration = math.ceil(num_words * word_time * 10) / 10
      return duration

def table_pdf(path):
  # read the PDF and detect the tables
  tables = tabula.read_pdf(path, pages="all", multiple_tables=True)
  df = tables[0]
  df_ = tables[1]
  for j in range(len(df.columns)):
    print(j)
    if j == (len(df.columns)-1):
      pass
    else:
      df = df.rename(columns={df.columns[j]: 'speaker', df.columns[j+1]: 'text'})
  for j in range(len(df_.columns)):
    if j == (len(df.columns)-1):
      pass
    else:
      df_ = df_.rename(columns={df_.columns[j]: 'speaker', df_.columns[j+1]: 'text'})
  df_full = pd.concat([df,df_])
  word_time = 0.5

  # create a function to calculate the duration of each sentence (in seconds)

  # apply the function to the text column to create a duration column
  df_full['duration'] = df_full['text'].apply(calculate_duration)

  # create the start and end time columns based on the duration column
  start_time = 0
  for i, row in df_full.iterrows():
      duration = row['duration']
      end_time = start_time + duration
      df_full.at[i, 'start_time'] = start_time
      df_full.at[i, 'end_time'] = end_time
      start_time = end_time

  # display the final dataframe
  df_full

  return df_full

data = table_pdf('/content/Script for Basic Business Meeting.pdf')

data
