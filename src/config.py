import os
from dotenv import load_dotenv

load_dotenv()

SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_API_KEY")
BLOB_STORAGE_CONNECTION_STRING = os.getenv("BLOB_STORAGE_CONNECTION_STRING")
BLOB_STORAGE_CONTAINER_NAME =os.getenv("BLOB_STORAGE_CONTAINER_NAME")
SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")
SEARCH_SERVICE_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
SEARCH_INDEXER_NAME = os.getenv("SEARCH_INDEXER_NAME")
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
API_KEY = os.getenv('API_KEY')
AZURE_OPENAI_API_VERSION = "2023-03-15-preview"
SEARCH_MIN_SCORE_THRESHOLD=2
LLM_MODEL = "gpt-4o-mini"
ALLOWED_LLM_MODEL = ["gpt-35-turbo", "gpt-4o", "gpt-4o-mini"]
ALLOWED_DOCUMENT_MODELS = ["prebuilt-layout", "prebuilt-read"]
AZURE_ENDPOINT=os.getenv('AZURE_ENDPOINT')
AZURE_KEY=os.getenv('AZURE_KEY')




PDF_STORAGE_CONTAINER_NAME='pdf-storage'
PDF_INDEX_NAME = 'pdf-index'

def get_gosure_base_url():
    return os.environ.get("GOSURE_BASE_URL")


def get_gosure_tenant():
    return os.environ.get("GOSURE_TENANT")


def get_gosure_tenant_username():
    return os.environ.get("GOSURE_TENANT_USERNAME")


def get_gosure_tenant_password():
    return os.environ.get("GOSURE_TENANT_PASSWORD")
