import os
import tempfile
from files import file_uploader, url_uploader
from question import chat_with_doc
from brain import brain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from supabase import Client, create_client

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


print("🧠 Blokument Brain  🧠")
print("Store your knowledge in a vector store and query it with OpenAI's GPT-3/4.\n")

user_choice = input("Choose an action (Add Knowledge, Chat with your Brain, Forget, Explore): ")

if user_choice == 'Add Knowledge':
    print("\nAdding Knowledge")
    file_uploader(supabase, openai_api_key, vector_store)
elif user_choice == 'Chat with your Brain':
    print("\nChatting with your Brain")
    chat_with_doc(models[0], vector_store, stats_db=supabase, question)
elif user_choice == 'Forget':
    print("\nForgetting")
    brain(supabase)
elif user_choice == 'Explore':
    print("\nExploring")
    view_document(supabase)
else:
    print(f"Invalid choice: {user_choice}. Please choose from the given options.")
