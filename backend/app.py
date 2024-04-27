import os
import pickle

from markupsafe import escape
from constants import app_constant as constants
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS, cross_origin


from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from huggingface_hub import login
login("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")


app = Flask(__name__)
CORS(app, origins=['http://localhost:4200/'])

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/prompt/recommendation', methods=['POST'])
@cross_origin(supports_credentials=True)
def generate_recommendation_prompt():
  req = request.json
  question = req['question']
  document_data = find_documents(question)
  abstracts = get_abstracts(document_data)
  prompt = create_recommendation_prompt(question, abstracts)
  return jsonify({'prompt' : prompt})


@app.route('/prompt/qa', methods=['POST'])
def generate_qa_prompt():
  req = request.json
  question = req['question']
  document_data = find_documents(question)
  prompt = create_qa_prompt(question, document_data)
  print("Document: ", document_data)
  print("Prompt: ", prompt)
  response = jsonify({
    'prompt' : prompt,
    'context': document_data
  })
  return response

# mock api route
@app.route('/documents', methods=['GET'])
def get_docs():
  question = "What factors control the ability of palladium cathodes to attain high loading levels?"
  document_data = find_documents(question)
  abstracts = get_abstracts(document_data)
  prompt = create_recommendation_prompt(question, abstracts)
  return jsonify({'prompt' : prompt})


@app.route('/qa', methods=['GET'])
def get_qa():
  question = request.args.get('question')
  document_data = find_documents(question)
  prompt = create_qa_prompt(question, document_data)
  print("Document: ", document_data)
  print("Prompt: ", prompt)
  response = jsonify({
    'prompt' : prompt,
    'context': document_data
  })
  return response


# @app.route("/data", methods=['POST'])
# def data():
#     server = constants.app_constant['cpp_server']
#     url = server + "/completion"
    
#     prompt_text = request.json['prompt']
#     print(prompt_text)
#     data =  {
#         "prompt": prompt_text,
#         "n_predict": 1024,
#         "stream": True
#     }
#     headers = {'Content-type': 'application/json'}
#     response = requests.post(url, data=json.dumps(data), headers=headers, stream=True)
    
#     def stream():
#         for chunk in response.iter_content(chunk_size=10):
#             print(chunk)
#             yield chunk

#     return stream()


def find_documents(question):
  persist_directory = constants['persist_directory']
  embedding_model = constants['embedding_model']
  dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', persist_directory))
  embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
  vector_db = Chroma(persist_directory=dir, embedding_function=embeddings)
  result_docs = vector_db.similarity_search(question, k=5)

  docs = []
  doc_count = 0
  for doc in result_docs:
    print(doc)
    obj = {
      'page_content' : process_text(doc.page_content),
      'metadata': {
        'doc_id': doc.metadata['doc_id'],
        'title' : process_text(doc.metadata['title'])
      }
    }
    docs.append(obj)
    doc_count += 1
  
  data = {
    'doc_count': doc_count,
    'documents': docs
  }
  
  return data

def get_abstracts(document_data):
  candidates = {}
  for doc in document_data['documents']:
      md = (doc['metadata'])
      candidates[md['doc_id']] = 1
  
  dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'src', 'abstracts.pkl'))
  with open(dir, 'rb') as file:
    abstracts = pickle.load(file)
  
  candidate_abstracts = ""
  for id in candidates:
    processed_abstract = abstracts[id - 1][0:300]
    processed_abstract = process_text(processed_abstract)
    candidate_abstracts += f"\n\n Doc{id}.pdf: {processed_abstract};"
  
  return candidate_abstracts

def process_text(text):
  processed_text = text.replace('\n','')
  processed_text = processed_text.replace('\t','')
  processed_text = processed_text.strip()
  return processed_text

def create_qa_prompt(question, context):
  prompt = f""" [INST] Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer. Keep the answer as concise as possible.
    Context: {context}
    Question: {question}
    Helpful Answer:
  """
  return prompt


def create_recommendation_prompt(question, abstracts):
  prompt = f""" [INST] You are a recommendation system which recommends papers based on search. Given below are the following.
    1. The prompt from user 
    2. The candidate papers and its incomplete abstract seperated by semicolon.
    Give recommendation of top 3 papers and insights about these candidates for future research.
    User prompt: {question} 
    Candidates: {abstracts} 
    [/INST]
    """
  return prompt

if __name__ == '__main__':
    app.run(debug=True)