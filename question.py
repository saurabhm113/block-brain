from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import SupabaseVectorStore
import os
import json
import logging
from prompt import *

openai_api_key = os.environ['OPENAI_API_KEY']
logger = logging.getLogger(__name__)
modelai = OpenAI(
        max_tokens=555
    )

#pass question to query
def chat_with_doc(model, vector_store: SupabaseVectorStore, stats_db, question, chain_type_kwargs=chain_type_kwargs_default):            
            # Get the retriever from the vector store
            retriever = vector_store.as_retriever()

            # Load the QA chain
            qa = RetrievalQA.from_chain_type(llm=modelai, chain_type="stuff", retriever=retriever, chain_type_kwargs=chain_type_kwargs_default)

            # Generate model's response
            model_response = qa.run(question)
            logger.info('Result: %s', model_response)
            
            #print(model_response)
            return model_response

#pass question to query for predict
def chat_with_doc_predict(model, vector_store: SupabaseVectorStore, stats_db, question, chain_type_kwargs=chain_type_kwargs_predict):            
            # Get the retriever from the vector store
            retriever = vector_store.as_retriever()

            # Load the QA chain
            qa = RetrievalQA.from_chain_type(llm=modelai, chain_type="stuff", retriever=retriever, chain_type_kwargs=chain_type_kwargs_predict)

            # Generate model's response
            model_response = qa.run(question)
            logger.info('Result: %s', model_response)
            
            #print(model_response)
            return model_response