import os
import json

from constants import app_constant as constants
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS, cross_origin

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from huggingface_hub import login
login("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")


app = Flask(__name__)
CORS(app, origins=['http://localhost:4200/', 'http://localhost:8080/'])

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/recommendation', methods=['GET'])
def generate_recommendation_prompt():
  question = request.args.get('question')
  document_data = find_documents(question)
  documents = get_documents_with_abstracts(document_data)
  prompt = create_recommendation_prompt(question, documents)
  return jsonify({
    'prompt' : prompt,
    'documentList': documents
  })


@app.route('/qa', methods=['GET'])
def get_qa():
  question = request.args.get('question')
  document_data = find_documents(question)
  prompt = create_qa_prompt(question, document_data)
  response = jsonify({
    'prompt' : prompt,
    'context': document_data
  })
  return response


def find_documents(question):
  persist_directory = constants['persist_directory']
  embedding_model = constants['embedding_model']
  dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', persist_directory))
  embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
  vector_db = Chroma(persist_directory=dir, embedding_function=embeddings)
  result_docs = vector_db.similarity_search(question, k=3)

  with open('stockDataset.json', 'rb') as file:
    dataset = json.load(file)

  docs = []
  doc_count = 0
  for doc in result_docs:
    obj = {
      'page_content' : process_text(doc.page_content),
      'metadata': {
        'doc_id': doc.metadata['doc_id'],
        'title' : process_text(doc.metadata['title']),
        'link': dataset[doc.metadata['doc_id']-1]['link']
      }
    }
    docs.append(obj)
    doc_count += 1
  
  data = {
    'doc_count': doc_count,
    'documents': docs
  }
  
  return data

def get_documents_with_abstracts(document_data):
  finalDocuments = []
  with open('stockDataset.json', 'rb') as file:
    dataset = json.load(file)
  
  for doc in document_data['documents']:
    docObject = {
      'doc_id': doc['metadata']['doc_id'],
      'title': doc['metadata']['title'],
      'abstract': dataset[doc['metadata']['doc_id']-1]['abstract'],
      'link': dataset[doc['metadata']['doc_id']-1]['link']
    }
    finalDocuments.append(docObject)
  
  return finalDocuments

def process_text(text):
  processed_text = text.replace('\n','')
  processed_text = processed_text.replace('\t','')
  processed_text = processed_text.strip()
  return processed_text

def create_qa_prompt(question, context):
  prompt = f"""Use the following pieces of articles to answer the question at the end.
    For each article, you are provided with the docId, title and its page content. You need to use the information of the title and the page content for your response.
    If you have any prior information about that article, you can use that in framing the answer.
    If you don't know the answer, just say that you don't know, don't try to make up an answer. Keep the answer as meaningful as possible.
  """
  prompt_2 = ""
  for doc in context['documents']:
    prompt_2 += f"""DocId: {doc['metadata']['doc_id']}
    Title: {doc['metadata']['title']}
    Page Content: {doc['page_content']}
    """
  
  questionPrompt = f"""
    Question: {question}
    Helpful Answer: 
    """
  finalPrompt = prompt + prompt_2 + questionPrompt
  return finalPrompt

def create_recommendation_prompt(question, documents):
  prompt = f"""You are a recommendation system which recommends why certain papers are referred based on search. You are given the following things:
    1. The question asked by the user 
    2. The top 3 best papers relevant to the user question and for each paper, you are given its docId, title, and abstract.
    Return a brief summary of the user's question based on the research papers provided and their corresponding title and abstract.
    Along with this, also state why each of these papers is relevant to the question asked by the user.
    User Question: {question}
    Papers:
    """
  
  documentsPrompt = ""
  for doc in documents:
    documentsPrompt += f"""DocId: {doc['doc_id']}
    Title: {doc['title']}
    Abstract: {doc['abstract']}
    """
  return prompt + documentsPrompt

if __name__ == '__main__':
    app.run(port=3000)