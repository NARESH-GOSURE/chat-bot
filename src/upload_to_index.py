from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from .config import SEARCH_ADMIN_KEY, SEARCH_SERVICE_ENDPOINT
import json
from .config import BLOB_STORAGE_CONNECTION_STRING,PDF_STORAGE_CONTAINER_NAME,PDF_INDEX_NAME
from azure.storage.blob import BlobServiceClient
from .data_storage_connection import check_indexer_status_and_run

search_client = SearchClient(endpoint=SEARCH_SERVICE_ENDPOINT, 
                                 index_name=PDF_INDEX_NAME, 
                                 credential=AzureKeyCredential(SEARCH_ADMIN_KEY))
blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)


def get_chuncked_json_output(pdf_chunk_name):
    documents =[]
    blob_client = blob_service_client.get_blob_client(container=PDF_STORAGE_CONTAINER_NAME, blob=pdf_chunk_name)
    blob_data = blob_client.download_blob()
    json_content = blob_data.readall().decode("utf-8")
    documents = json.loads(json_content)
    if isinstance(documents, list):
        documents = [doc for doc in documents if isinstance(doc, dict)]
    
    return documents

   
def fetch_and_view_blobs(container_name):
    container_client = blob_service_client.get_container_client(container_name)
    print(f"Listing blobs in container: {container_name}")
    blobs = container_client.list_blobs()
    for blob in blobs:
        blob_name = blob.name
        print(f"Fetching blob: {blob_name}")
        blob_client = container_client.get_blob_client(blob_name)
        blob_data = blob_client.download_blob()
        content = blob_data.readall()


# fetch_and_view_blobs("pdf-storage")
# fetch_and_view_blobs("raw-doc")
# fetch_and_view_blobs("chunks-storage")



    
def batch_documents(documents, batch_size=100):
    for i in range(0, len(documents), batch_size):
        yield documents[i:i + batch_size]

def index_documents_in_batches(documents, batch_size=100):
    for batch in batch_documents(documents, batch_size):
        try:
            results = search_client.upload_documents(documents=batch)
            for result in results:
                if result.succeeded:
                    print(f"Document {result.key} indexed successfully.")
                else:
                    print(f"Failed to index document {result.key}: {result.error_message}")
        except Exception as e:
            print(f"Error indexing batch: {e}")

def upload_to_index(pdf_chunks_name):
    chunks = get_chuncked_json_output(pdf_chunks_name)
    index_documents_in_batches(chunks)
    check_indexer_status_and_run()
