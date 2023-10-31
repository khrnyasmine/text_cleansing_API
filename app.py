"""
Flask API Application
"""
from flask import Flask, jsonify, request, Markup
import pandas as pd
from time import perf_counter
from flasgger import Swagger, swag_from, LazyString, LazyJSONEncoder
from db import (
    create_connection, insert_dictionary_to_db, 
    insert_result_to_db, show_cleansing_result,
    insert_upload_result_to_db,
)
from cleansing_function import (
    text_cleansing, cleansing_files,
)

# Prevent sorting keys in JSON response
import flask
flask.json.provider.DefaultJSONProvider.sort_keys = False

# Set Up Database
db_connection = create_connection()
insert_dictionary_to_db(db_connection)
db_connection.close()

# Initialize flask application
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# Assign LazyJSONEncoder to app.json_encoder for swagger UI
app.json_encoder = LazyJSONEncoder
# Create swagger config & swagger template
swagger_template = {
    "info": {
        "title": LazyString(lambda: "Text Cleansing API"),
        "version": LazyString(lambda: "1.0.0"),
        "description": LazyString(lambda: "Dokumentasi API untuk membersihkan text"),
    },
    "host": LazyString(lambda: request.host)
}
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
    }
# Initialize Swagger from swagger template & config
Swagger = Swagger(app, template=swagger_template, config=swagger_config)

# Homepage
@swag_from('docs/home.yml', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
    welcome_msg = {
        "version": "1.0.0",
        "message": "Welcome to Flask API",
        "author": "Khairina Yasmine"
    }
    return jsonify(welcome_msg)

# Show cleansing result
@swag_from('docs/show_cleansing_result.yml', methods=['GET'])
@app.route('/show_cleansing_result', methods=['GET'])
def show_cleansing_result_api():
    db_connection = create_connection()
    cleansing_result = show_cleansing_result(db_connection)
    return jsonify(cleansing_result)

# Cleansing text using form
@swag_from('docs/cleansing_form.yml', methods=['POST'])
@app.route('/cleansing_form', methods=['POST'])
def cleansing_form():
    # Get text from input user
    raw_text = request.form["raw_text"]

    # Cleaning text data
    start = perf_counter()
    clean_text = text_cleansing(raw_text)
    end = perf_counter()
    time_elapse = end - start
    print(f"Processing time: {time_elapse} second")

    result_response = {"raw_text": raw_text, "clean_text": clean_text, "processing_time": time_elapse}
    
    # Insert result to database
    db_connection = create_connection()
    insert_result_to_db(db_connection, raw_text, clean_text)
    return jsonify(result_response)

# Cleansing text using csv upload
@swag_from('docs/cleansing_upload.yml', methods=['POST'])
@app.route('/cleansing_upload', methods=['POST'])
def cleansing_upload():
    # Get file from upload to dataframe
    uploaded_file = request.files['upload_file']
    # Read csv file upload, jika
    df_upload = pd.read_csv(uploaded_file, encoding="latin-1")
    # Read csv file to dataframe then cleansing
    start = perf_counter()
    df_cleansing = cleansing_files(df_upload)
    end = perf_counter()
    time_elapse = end - start
    print(f"Processing time: {time_elapse} second")
    # Upload result to database
    db_connection = create_connection()
    insert_upload_result_to_db(db_connection, df_cleansing)
    print("Upload result to database success!")
    print_result = df_cleansing[["raw_text", "clean_text"]]
    result_response = print_result.T.to_dict()
    return jsonify(result_response)

if __name__ == '__main__':
    app.run()
