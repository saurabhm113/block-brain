from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import SupabaseVectorStore
import os
import json
import logging

openai_api_key = os.environ['OPENAI_API_KEY']
logger = logging.getLogger(__name__)
modelai = OpenAI(
        max_tokens=555
    )
#pass question to query
def chat_with_doc(model, vector_store: SupabaseVectorStore, stats_db, question):            
            # Get the retriever from the vector store
            retriever = vector_store.as_retriever()

            # Load the QA chain
            qa = RetrievalQA.from_chain_type(llm=modelai, chain_type="stuff", retriever=retriever)

            # Generate model's response
            model_response = qa.run(question)
            logger.info('Result: %s', model_response)

            print(model_response)
            return model_response
