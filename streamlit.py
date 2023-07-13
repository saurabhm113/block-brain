import streamlit as st
import os
import json
import logging
from pydantic import BaseModel, HttpUrl

from question import chat_with_doc, chat_with_doc_predict
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from supabase import Client, create_client
from loaders.html import get_content, HTMLRetrievalError, FileWritingError, UnexpectedError

supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
openai_api_key = os.environ["OPENAI_API_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

vector_store = SupabaseVectorStore(
    supabase, embeddings, table_name="documents")
models = ["gpt-3.5-turbo", "gpt-4"]
question = "summerise"

def load_youtube_video(video_url):
    loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
    response = loader.load()

    document = response[0]

    response_dict = {
        "title": document.metadata['title'],
        "page_content": document.page_content,
    }

    file_path = temp_file(response_dict["title"], response_dict["page_content"])

    file_uploader(file_path, supabase, openai_api_key, vector_store)

    return response_dict

def query_with_doc(topic):
    question = topic
    chat_response = chat_with_doc(models[0], vector_store, stats_db=supabase, question=question)

    start_index = chat_response.find("{")
    end_index = chat_response.rfind("}")
    json_str = chat_response[start_index:end_index+1]

    chat_response_dict = json.loads(json_str)

    return chat_response_dict

def embed_url(url):
    try:
        file_path = get_content(url)
        result = file_uploader(file_path, supabase, openai_api_key, vector_store)
        result_dict = json.loads(result)
        status = result_dict["status"]
        return status
    except HTMLRetrievalError as e:
        return {"error": "Failed to retrieve HTML from the given URL."}
    except FileWritingError as e:
        return {"error": "Failed to write HTML content to file."}
    except UnexpectedError as e:
        return {"error": "An unexpected error occurred while processing the request."}

def query_with_doc_predict(topic):
    question = topic
    chat_response = chat_with_doc_predict(models[0], vector_store, stats_db=supabase, question=question)

    start_index = chat_response.find("{")
    end_index = chat_response.rfind("}")
    json_str = chat_response[start_index:end_index+1]

    chat_response_dict = json.loads(json_str)

    return chat_response_dict

# Streamlit app
def main():
    st.title('OpenAI Application')

    option = st.selectbox(
        'Choose a function',
        ('query', 'query_predict', 'youtuburl', 'url_embed')
    )

    if option == 'query':
        topic = st.text_input('Enter a topic')
        if st.button('Run Query'):
            response = query_with_doc(topic)
            st.write(response)

    elif option == 'query_predict':
        topic = st.text_input('Enter a topic')
        if st.button('Run Query Predict'):
            response = query_with_doc_predict(topic)
            st.write(response)

    elif option == 'youtuburl':
        video_url = st.text_input('Enter a YouTube URL')
        if st.button('Load YouTube Video'):
            response = load_youtube_video(video_url)
            st.write(response)

    elif option == 'url_embed':
        url = st.text_input('Enter a URL')
        if st.button('Embed URL'):
            response = embed_url(url)
            st.write(response)

if __name__ == "__main__":
    main()
