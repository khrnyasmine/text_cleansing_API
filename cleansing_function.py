"""
Function untuk membersihkan data text
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

# fungsi untuk membersihkan kata alay
def alay_cleansing(text):
    for key, value in kamus_alay_dict.items():
        if key == text:
            text = text.replace(key, value)
    return text 

# fungsi untuk mencensor kata abusive
def abusive_cleansing(text):
    for word in abusive_data['ABUSIVE']:
        if word == text:
            text = text.replace(word, word[0] + '*' * (len(word)-1))
    return text

# untuk mencatat kemunculan kata abusive
abusive_occurence = []

def count_abusive(text):
    jumlah_kata_abusive = 0
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(text)).lower()
    words = text.split()
    for word in words:
        for item in abusive_data['ABUSIVE']:
            if item == word:
                jumlah_kata_abusive += 1
                abusive_occurence.append(word)
    return jumlah_kata_abusive

def text_cleansing(text):
    # lowercase
    clean_text = str(text).lower()
    # membersihkan URL
    clean_text = re.sub(r'(http\S+|www\S+)', '', clean_text).strip()
    # bersihkan tanda baca (selain huruf dan angka)
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', clean_text)
    # membersihkan username
    clean_text = re.sub('user',' ',clean_text)
    # mensubtitusikan kata alay dengan kata baku
    clean_text = ' '.join([alay_cleansing(j) for j in clean_text.split()])
    # mencensor kata abusive
    clean_text = ' '.join([abusive_cleansing(i) for i in clean_text.split()])
    clean_text = re.sub('uniform resource locator',' ',clean_text).strip()
    return clean_text

def cleansing_files(file_upload):
    # Ambil hanya kolom pertama saja
    df_upload = pd.DataFrame(file_upload.iloc[:,0])
    
    # Rename kolom menjadi "raw_text"
    df_upload.columns = ["raw_text"]

    # Bersihkan text menggunakan fungsi text_cleansing
    # Simpan di kolom "clean_text"
    df_upload["clean_text"] = df_upload["raw_text"].apply(text_cleansing)
    #df_upload["jumlah_kata_alay"] = df_upload["raw_text"].apply(count_alay)
    df_upload["jumlah_kata_abusive"] = df_upload["raw_text"].apply(count_abusive)
    print("Cleansing text success!")
    return df_upload