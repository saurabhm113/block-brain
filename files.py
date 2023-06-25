import os
from langchain.document_loaders import YoutubeLoader
#from loaders.audio import process_audio
from loaders.txt import process_txt
# from loaders.csv import process_csv
# from loaders.markdown import process_markdown
# from loaders.html import process_html
# from utils import compute_sha1_from_content
# from loaders.pdf import process_pdf
# from loaders.html import get_html, create_html_file, delete_tempfile
# from loaders.powerpoint import process_powerpoint
# from loaders.docx import process_docx
import requests
import re
import unicodedata
import tempfile
from utils import compute_sha1_from_file, compute_sha1_from_content

file_processors = {
    ".txt": process_txt,
    # ".csv": process_csv,
    # ".md": process_markdown,
    # ".markdown": process_markdown,
    # ".m4a": process_audio,
    # ".mp3": process_audio,
    # ".webm": process_audio,
    # ".mp4": process_audio,
    # ".mpga": process_audio,
    # ".wav": process_audio,
    # ".mpeg": process_audio,
    # ".pdf": process_pdf,
    # ".html": process_html,
    #  ".pptx": process_powerpoint,
    #  ".docx": process_docx
}

def file_already_exists(supabase, file_path):
    file_sha1 = compute_sha1_from_file(file_path)
    response = supabase.table("documents").select("id").eq("metadata->>file_sha1", file_sha1).execute()
    return len(response.data) > 0


def filter_file(file, supabase, vector_store):
    if file_already_exists(supabase, file):
        print(f"😎 {file.name} is already in the database.")
        return False
    elif file.size < 1:
        print(f"💨 {file.name} is empty.")
        return False
    else:
        file_extension = os.path.splitext(file.name)[-1]
        if file_extension in file_processors:
            if self_hosted == "false":
                file_processors[file_extension](vector_store, file, stats_db=supabase)
            else:
                file_processors[file_extension](vector_store, file, stats_db=None)
            print(f"✅ {file.name} ")
            return True
        else:
            print(f"❌ {file.name} is not a valid file type.")
            return False

def file_uploader(file_path, supabase, openai_api_key, vector_store):
    # Check if the file already exists in the database
    if file_already_exists(supabase, file_path):
        print(f"😎 {os.path.basename(file_path)} is already in the database.")
        return False
    else:
        # Get the file extension
        file_extension = os.path.splitext(file_path)[-1]
        if file_extension in file_processors:
            # Open the file and process it
            with open(file_path, 'rb') as file:
                file_processors[file_extension](vector_store, file, stats_db=supabase)
            print(f"✅ {os.path.basename(file_path)} ")
            return True
        else:
            print(f"❌ {os.path.basename(file_path)} is not a valid file type.")
            return False

# def url_uploader(url, supabase, vector_store):
#     loader = YoutubeLoader.from_youtube_url(url, add_video_info=False)
