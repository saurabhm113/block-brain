from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import SupabaseVectorStore
import os
import json
import logging
from langchain.prompts import PromptTemplate

openai_api_key = os.environ['OPENAI_API_KEY']
logger = logging.getLogger(__name__)
modelai = OpenAI(
        max_tokens=555
    )

#Prompt Template
prompt_template_default = """Use the following pieces of context to answer the question at the end.You are a capable assistant tasked with providing only the necessary information, without any introductory phrases or additional comments.
Your task is to generate one trivia questions about given topic. Each question should have four options, and you should specify which option is correct for each question. If you cannot answer a question, simply respond with 'ask something else'.
Do not provide any explanation about your training or capabilities, and do not fabricate an answer if you don't know the correct response. Your responses should directly address the question asked. If a user question is unrelated to the context established by the system, 
your response should be 'out of context' in json as follow:
{{
    "model_error": "topic out of context"
}}
Whatever your answer is Your responses should be structured as follows in json only remove anything outof json object:
{{
"question": "Your trivia question here?",
"options": ["Option 1", "Option 2", "Option 3", "Option 4"],
"correct_answer": "correct answer"
}}

For example:
{{
        "question": "Which university in Kentucky has a football team?",
        "options": [
            "University of Louisville",
            "University of Kentucky",
            "Western Kentucky University",
            "Murray State University"
        ],
        "correct_answer": "University of Kentucky"
}}

And not like below:
What is the maximum number of players allowed on a basketball court at one time?
{{
    "question": "What is the maximum number of players allowed on a basketball court at one time?",
    "options": ["5", "6", "7", "8"],
    "correct_answer": "5"

}}

{context}

Question: {question}
"""


PROMPT_DEFAULT = PromptTemplate(
    template=prompt_template_default, input_variables=["context", "question"]
)

chain_type_kwargs_default = {"prompt": PROMPT_DEFAULT}

#Prompt Template
prompt_template_predict = """Use the following pieces of context to answer the question at the end.You are a capable assistant tasked with providing only the necessary information, without any introductory phrases or additional comments.
Your task is to generate one prediction questions about given topic. Each question should have four options, and you should specify which option is correct for each question. If you cannot answer a question, simply respond with 'ask something else'.
Do not provide any explanation about your training or capabilities, and do not fabricate an answer if you don't know the correct response. Your responses should directly address the question asked. If a user question is unrelated to the context established by the system, 
your response should be 'out of context' in json as follow:
{{
    "model_error": "topic out of context"
}}
Whatever your answer is Your responses should be structured as follows in json only remove anything outof json object:
{{
"question": "Your prediction question here?",
"options": ["Option 1", "Option 2", "Option 3", "Option 4"]
}}

For example:
{{
        "question": "Which team is currently the favorite to win the 2024 NBA title?",
        "options": [
            "Boston Celtics",
            "Denver Nuggets",
            "Milwaukee Bucks",
            "Phoenix Suns"
        ]
}}

And not like below:
Which team is favored to win the 2024 NBA Finals??
{{
    "question": "Which team is favored to win the 2024 NBA Finals?",
    "options": [
            "Boston Celtics",
            "Denver Nuggets",
            "Milwaukee Bucks",
            "Phoenix Suns"
        ]
}}

{context}

Question: {question}
"""

PROMPT_PREDICT = PromptTemplate(
    template=prompt_template_predict, input_variables=["context", "question"]
)

chain_type_kwargs_predict = {"prompt": PROMPT_PREDICT}

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