from .common import process_file
from langchain.document_loaders import TextLoader
import os

def process_txt(vector_store, file, stats_db):
    file_size = os.path.getsize(file.name)
    return process_file(vector_store, file, TextLoader, ".txt", file_size, stats_db=stats_db)