import os
from azure.storage.blob import BlobServiceClient
import json
from .config import BLOB_STORAGE_CONNECTION_STRING,PDF_STORAGE_CONTAINER_NAME

blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)



def upload(file):
    blob_name = file.filename
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(PDF_STORAGE_CONTAINER_NAME)
    blob_client = container_client.get_blob_client(f"{blob_name}")
    blob_client.upload_blob(file, overwrite=True)
    print(f"Uploaded {file.filename} to Azure Blob Storage.")
    return blob_name


def get_pdf_from_blob(container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    download_stream = blob_client.download_blob()
    return download_stream.readall()


def upload_chunks_to_azure_blob(chunks,pdf_file_name):
    new_pdf_file_name = pdf_file_name.replace('.', '_')
    BLOB_NAME = f"{new_pdf_file_name}_chunks.json"
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(PDF_STORAGE_CONTAINER_NAME)

    try:
        container_client.create_container()
    except Exception as e:
        print(f"Container already exists or overwritting the existing data into the container")
    
    json_data = json.dumps(chunks, indent=4)
    blob_client = container_client.get_blob_client(BLOB_NAME)

    blob_client.upload_blob(json_data, overwrite=True)
    print(f"Data successfully uploaded to blob: {BLOB_NAME}")
    return BLOB_NAME


# upload_chunks_to_azure_blob()

def container_lists():
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)
    try:
        containers = blob_service_client.list_containers()
        for container in containers:
            print(f"Container Name: {container['name']}")
    except Exception as e:
        print(f"Error occurred: {e}")
# container_lists()

def delete_blob_container(CONTAINER_NAME):
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)
    try:
        blob_service_client.delete_container(CONTAINER_NAME)
        print(f"Container '{CONTAINER_NAME}' has been deleted successfully.")
    except Exception as e:
        print(f"Error occurred while deleting container '{CONTAINER_NAME}': {e}")
# delete_blob_container('chunks-storage')



# if __name__ == "__main__":
#     from werkzeug.datastructures import FileStorage

#     file_path = "poly.pdf"
#     if os.path.exists(file_path):
#         with open(file_path, "rb") as f:
#             file = FileStorage(f, filename="poly.pdf")
#             upload(file)
#     else:
#         print("File not found. Make sure the PDF file exists.")


