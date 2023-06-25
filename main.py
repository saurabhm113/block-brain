import os
import tempfile
import json
from files import file_uploader
from question import chat_with_doc
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from supabase import Client, create_client
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from langchain.document_loaders import YoutubeLoader
from fastapi.responses import JSONResponse


from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

# Define a Pydantic model for the request body
class Video(BaseModel):
    video_url: HttpUrl

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

@app.post("/YouTubeURL")
async def load_youtube_video(video: Video):
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
    return response_dict
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query_with_doc(request: QueryRequest):
    question = request.query

    # Call chat_with_doc function and store the response
    chat_response = chat_with_doc(models[0], vector_store, stats_db=supabase, question=question)

    print(chat_response)

    # Create a dictionary with the chat response
    response_dict = {"chat_response": chat_response}

    # Return the response as JSON
    return JSONResponse(content=response_dict)
