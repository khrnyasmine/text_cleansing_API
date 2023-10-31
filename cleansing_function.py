"""
Function for data text cleansing
"""

import re
import pandas as pd

# import csv
# kamus abusive
abusive_data = pd.read_csv("csv_data/abusive.csv")
# kamus alay
kamus_alay_data = pd.read_csv("csv_data/alay.csv", encoding="latin-1")
kamus_alay_data.columns = ['alay', 'baku']
kamus_alay_dict = dict(zip(kamus_alay_data['alay'], kamus_alay_data['baku']))

# function to replace alay words to formal words
def alay_cleansing(text):
    for key, value in kamus_alay_dict.items():
        if key == text:
            text = text.replace(key, value)
    return text 

# function to censor abusive words
def abusive_cleansing(text):
    for word in abusive_data['ABUSIVE']:
        if word == text:
            text = text.replace(word, word[0] + '*' * (len(word)-1))
    return text

# function for text cleansing
def text_cleansing(text):
    # lowercase
    clean_text = str(text).lower()
    # clean URL
    clean_text = re.sub(r'(http\S+|www\S+)', '', clean_text).strip()
    # clean emoticon byte
    clean_text = clean_text.replace("\\", " ")
    clean_text = re.sub(r'\bx[0-9a-fA-F]{2,}', ' ', clean_text)
    clean_text = re.sub(r'\bn\b', ' ', clean_text)
    clean_text = re.sub('\\+', ' ', clean_text)
    clean_text = re.sub('  +', ' ', clean_text)
    # clean punctuations
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', clean_text)
    # clean username
    clean_text = re.sub(r'\buser\b', '', clean_text, flags=re.IGNORECASE)
    # clean rt (retweet)
    clean_text = re.sub(r'\brt\b', '', clean_text, flags=re.IGNORECASE)
    # subtitute alay word with formal word
    clean_text = ' '.join([alay_cleansing(j) for j in clean_text.split()])
    # censor abusive word
    clean_text = ' '.join([abusive_cleansing(i) for i in clean_text.split()])
    # clean url
    clean_text = re.sub('uniform resource locator',' ',clean_text).strip()
    return clean_text


def cleansing_files(file_upload):
    # Get only the first column
    df_upload = pd.DataFrame(file_upload.iloc[:,0])
    
    # Rename column to "raw_text"
    df_upload.columns = ["raw_text"]

    # Clean text using text_cleansing function
    # Save result in "clean_text" column
    df_upload["clean_text"] = df_upload["raw_text"].apply(text_cleansing)
    print("Cleansing text success!")
    return df_upload