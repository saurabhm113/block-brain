import os
import tempfile
import json
import logging
import auth 
from files import file_uploader
from question import chat_with_doc, chat_with_doc_predict
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from supabase import Client, create_client
from pydantic import BaseModel, HttpUrl
from langchain.document_loaders import YoutubeLoader
from loaders.html import get_content, HTMLRetrievalError, FileWritingError, UnexpectedError


from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, HttpUrl



# Global variables
page_content = ""
title = ""
file_path = ""
app = FastAPI()

supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
openai_api_key = os.environ["OPENAI_API_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

vector_store = SupabaseVectorStore(
    supabase, embeddings, table_name="documents")
models = ["gpt-3.5-turbo", "gpt-4"]
question = "summerise"

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins as needed
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

print("🧠 Blokument Brain  🧠")

def temp_file(title, page_content):
    # Replace any characters in title that are not suitable for filenames
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '.', '_')).rstrip()

    # Create the directory if it does not exist
    os.makedirs('tmp', exist_ok=True)
    
    # Define file path
    file_path = f'tmp/{safe_title}.txt'
    
    # Write page_content to a file in the tmp directory
    with open(f'tmp/{safe_title}.txt', 'w') as f:
        f.write(page_content)
    # Return the file path
    return file_path
# youtubeurl route 
# then get the transcribe of youtube video
# dump transcribe txt file to temp folder
# get to loader variable
# Define a Pydantic model for the request body

class Video(BaseModel):
    video_url: HttpUrl

@app.post("/YouTubeURL")
async def load_youtube_video(
    video: Video,
    x_api_key: str = Depends(auth.verify_api_key)):
    # Extract the video URL from the request body
    video_url = video.video_url

    # Load the video
    loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
    response = loader.load()

    # Since response is a list, we'll get the first item
    document = response[0]

    # Create a dictionary that only includes the title and the page_content
    response_dict = {
        "title": document.metadata['title'],
        "page_content": document.page_content,
    }

    # Call temp_file function to write the page_content to a file
    file_path = temp_file(response_dict["title"], response_dict["page_content"])

    # Call file_uploader function with the file path
    file_uploader(file_path, supabase, openai_api_key, vector_store)

    # Return the response
    return {
            'statusCode': 200,
            'body': response_dict
        }
    
class QueryRequest(BaseModel):
    topic: str

@app.post("/query")
async def query_with_doc(
    request: QueryRequest,
    x_api_key: str = Depends(auth.verify_api_key)):
    # Configure logging
    logging.basicConfig(level=logging.INFO)  # Set the desired log level   
    question = request.topic
    logging.info('Question: %s', question)
    # Call chat_with_doc function and store the response
    chat_response = chat_with_doc(models[0], vector_store, stats_db=supabase, question=question)
    # logging.info(chat_response)
    # # Convert the chat_response string to a JSON object (dictionary)
    # chat_response_dict = json.loads(chat_response)
     # Extract the JSON object from chat_response
    start_index = chat_response.find("{")  # Find the start index of the JSON object
    end_index = chat_response.rfind("}")  # Find the end index of the JSON object
    json_str = chat_response[start_index:end_index+1]  # Extract the JSON object string

    # Convert the JSON object string to a dictionary
    chat_response_dict = json.loads(json_str)


    # Return the response as JSON
    return {
        'statusCode': 200,
        'body': chat_response_dict
    }

class URL(BaseModel):
    url: str

@app.post("/url_embed")
async def ambed_url(
    request: URL,
    x_api_key: str = Depends(auth.verify_api_key)):
    try:
        url = request.url
        file_path = get_content(url)
        logging.info(file_path)
        # Call file_uploader function with the file path
        result = file_uploader(file_path, supabase, openai_api_key, vector_store)

        result_dict = json.loads(result)  # Parse the JSON-encoded string into a dictionary
        status = result_dict["status"]  # Extract the "status" value

        logging.info(status)
        # Return the response as JSON
        return {
            'statusCode': 200,
            'body': status
        }

    except HTMLRetrievalError as e:
        return {"error": "Failed to retrieve HTML from the given URL."}

    except FileWritingError as e:
        return {"error": "Failed to write HTML content to file."}

    except UnexpectedError as e:
        return {"error": "An unexpected error occurred while processing the request."}

class QueryRequest(BaseModel):
    topic: str

@app.post("/query_predict")
async def query_with_doc(
    request: QueryRequest,
    x_api_key: str = Depends(auth.verify_api_key)):
    # Configure logging
    logging.basicConfig(level=logging.INFO)  # Set the desired log level   
    question = request.topic
    logging.info('Question: %s', question)
    # Call chat_with_doc function and store the response
    chat_response = chat_with_doc_predict(models[0], vector_store, stats_db=supabase, question=question)
    # logging.info(chat_response)
    # # Convert the chat_response string to a JSON object (dictionary)
    # chat_response_dict = json.loads(chat_response)
     # Extract the JSON object from chat_response
    start_index = chat_response.find("{")  # Find the start index of the JSON object
    end_index = chat_response.rfind("}")  # Find the end index of the JSON object
    json_str = chat_response[start_index:end_index+1]  # Extract the JSON object string

    # Convert the JSON object string to a dictionary
    chat_response_dict = json.loads(json_str)


    # Return the response as JSON
    return {
        'statusCode': 200,
        'body': chat_response_dict
    }

