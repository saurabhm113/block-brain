# from .common import process_file
# from langchain.document_loaders import UnstructuredHTMLLoader
# import requests
# import re
# import unicodedata
# import tempfile
# import os
# import streamlit as st
# from streamlit.runtime.uploaded_file_manager import UploadedFileRec, UploadedFile

# def process_html(vector_store, file, stats_db):
#     return process_file(vector_store, file, UnstructuredHTMLLoader, ".html", stats_db=stats_db)


# def get_html(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.text
#     else:
#         return None

# def create_html_file(url, content):
#     file_name = slugify(url) + ".html"
#     temp_file_path = os.path.join(tempfile.gettempdir(), file_name)
#     with open(temp_file_path, 'w') as temp_file:
#         temp_file.write(content)

#     record = UploadedFileRec(id=None, name=file_name, type='text/html', data=open(temp_file_path, 'rb').read())
#     uploaded_file = UploadedFile(record)
    
#     return uploaded_file, temp_file_path

# def delete_tempfile(temp_file_path, url, ret):
#     try:
#         os.remove(temp_file_path)
#         if ret:
#             st.write(f"✅ Content saved... {url}  ")
#     except OSError as e:
#         print(f"Error while deleting the temporary file: {str(e)}")
#         if ret:
#             st.write(f"❌ Error while saving content... {url}  ")

# def slugify(text):
#     text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
#     text = re.sub(r'[^\w\s-]', '', text).strip().lower()
#     text = re.sub(r'[-\s]+', '-', text)
#     return text

import requests
import os
from datetime import datetime
from langchain.document_loaders import UnstructuredHTMLLoader
import tempfile
import logging

import re
import nltk
nltk.download('punkt')

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the desired log level

class HTMLRetrievalError(Exception):
    pass

class FileWritingError(Exception):
    pass

class UnexpectedError(Exception):
    pass

def get_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise HTMLRetrievalError(f"Failed to retrieve HTML. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise HTMLRetrievalError(f"An error occurred while retrieving the HTML: {str(e)}")

def put_file(content, filename):
    try:
        with open(filename, 'w') as file:
            file.write(content)
        return filename
    except IOError as e:
        raise FileWritingError(f"An error occurred while writing the file: {str(e)}")

def get_and_save_html(url, dir_path):
    try:
        result = get_html(url)
        
        if result is not None:
            
            os.makedirs(dir_path, exist_ok=True)
            
            # Sanitize the URL to make it suitable for use as a filename
            sanitized_url = re.sub(r'[^a-zA-Z0-9\-.]+', '', url)
            #logging.info(f"Sanitized URL: {sanitized_url}")
            filename = f"{dir_path}/file_{sanitized_url}.html"
            file_path = put_file(result, filename)
            
            if file_path is not None:
                print(f"HTML content has been written to {file_path}")
                
                return file_path
            else:
                raise FileWritingError("Failed to write HTML content to file")
        else:
            raise HTMLRetrievalError("Failed to retrieve page")
    except (HTMLRetrievalError, FileWritingError) as e:
        raise e
    except Exception as e:
        logging.info(f"inside exceptions:")
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")

def get_content(url):
    """Get and save HTML from a given web address"""
    
    try:
        file_path = get_and_save_html(url, "./html_doc")
        loader = UnstructuredHTMLLoader(file_path)
        data = loader.load()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(str(data[0].page_content).encode())
            logging.info(f"Data written to temporary file: {temp_file.name}")
            
            print(temp_file)
            return temp_file.name
    except (HTMLRetrievalError, FileWritingError, UnexpectedError) as e:
        raise e
    except Exception as e:
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")