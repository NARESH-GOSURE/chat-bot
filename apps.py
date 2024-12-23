from flask import Flask, request, jsonify
from flask_cors import CORS
from src.processing import upload_and_process_pdf_content
from src.cognitive_search import advanced_search

from src.config import API_KEY
from dotenv import load_dotenv
load_dotenv()


# Decorator to check the API key
def require_api_key(f):
    def wrap(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key and API_KEY and api_key == API_KEY:
            return f(*args, **kwargs)
        else:
            response = jsonify({"error": "Unauthorized, invalid or missing API key"})
            response.status_code = 401
            return response
    return wrap




apps = Flask(__name__)
CORS(apps)

@require_api_key
@apps.route('/pdf/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        
        pdf_name= upload_and_process_pdf_content(file)


        return jsonify({"message": f"Uploaded {pdf_name} to Azure Blob Storage and indexing is done {pdf_name}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@require_api_key
@apps.route('/advanced-search', methods=['GET'])
def search():
    query = request.args.get('query')
    file_name = request.args.get('file_name')
    
    if not query:
        return jsonify({"error": "Query text is required"}), 400
    
    if not file_name:
        return jsonify({"error": "File name is required"}), 400

    try:
        response=advanced_search(query_text=query,file_name=file_name)
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    apps.run(debug=True)
