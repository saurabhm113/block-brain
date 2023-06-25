import os
import tempfile
from files import file_uploader, url_uploader
from question import chat_with_doc
#from brain import brain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from supabase import Client, create_client
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from langchain.document_loaders import YoutubeLoader



supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
openai_api_key = os.environ["OPENAI_API_KEY"]
anthropic_api_key = os.environ["ANTHROPIC_API_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)
self_hosted = os.environ["SELF_HOSTED"]

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

vector_store = SupabaseVectorStore(
    supabase, embeddings, table_name="documents")
models = ["gpt-3.5-turbo", "gpt-4"]


app = FastAPI()


print("🧠 Blokument Brain  🧠")
print("Store your knowledge in a vector store and query it with OpenAI's GPT-3/4.\n")

user_choice = input("Choose an action (Add Knowledge, Chat with your Brain, Forget, Explore): ")


# youtubeurl route 
# then get the transcribe of youtube video
# dump transcribe txt file to temp folder
# get to loader variable

@app.post("/YouTubeURL/")
async def load_youtube_video(video_url: HttpUrl):
    # Assuming langchain's document loader function is 'load_document'
    # and it can handle YouTube URLs
    loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True, language=["en"], translation="en")
    file_uploader(HttpUrl, supabase, openai_api_key, vector_store)
    # handle the response from the Langchain API here
    # returning it as JSON for this example
    return loader.load()




if user_choice == 'Add Knowledge':
    print("\nAdding Knowledge")
    file_uploader(filepath, supabase, openai_api_key, vector_store)
elif user_choice == 'Chat with your Brain':
    print("\nChatting with your Brain")
    chat_with_doc(models[0], vector_store, stats_db=supabase, question)
#elif user_choice == 'Forget':
#    print("\nForgetting")
#    brain(supabase)
elif user_choice == 'Explore':
    print("\nExploring")
    view_document(supabase)
else:
    print(f"Invalid choice: {user_choice}. Please choose from the given options.")
