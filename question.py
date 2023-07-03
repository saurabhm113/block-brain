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
prompt_template = """Use the following pieces of context to answer the question at the end.You are a capable assistant tasked with providing only the necessary information, without any introductory phrases or additional comments.
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
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chain_type_kwargs = {"prompt": PROMPT}
#pass question to query
def chat_with_doc(model, vector_store: SupabaseVectorStore, stats_db, question):            
            # Get the retriever from the vector store
            retriever = vector_store.as_retriever()

            # Load the QA chain
            qa = RetrievalQA.from_chain_type(llm=modelai, chain_type="stuff", retriever=retriever, chain_type_kwargs=chain_type_kwargs)

            # Generate model's response
            model_response = qa.run(question)
            logger.info('Result: %s', model_response)
            
            #print(model_response)
            return model_response
