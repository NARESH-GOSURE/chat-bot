from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import SearchIndex, SearchIndexer, SimpleField, SearchableField, ComplexField,_edm as edm,SearchField,SearchFieldDataType
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import SearchIndexerDataSourceConnection
from .config import BLOB_STORAGE_CONNECTION_STRING,SEARCH_ADMIN_KEY, SEARCH_SERVICE_ENDPOINT


INDEX_NAME = "pdf-index"
INDEXER_NAME='pdf-indexer'
DATA_SOURCE_CONNECTION_NAME="pdf-data-source"

def delete_existing_resources():
    try:
        search_index_client = SearchIndexClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))
        existing_indexes = search_index_client.list_indexes()
        index_names = [index.name for index in existing_indexes]
        
        if INDEX_NAME in index_names:
            print(f"Index '{INDEX_NAME}' already exists..")
            search_index_client.delete_index(INDEX_NAME)
        else:
            print(f"INDEX NAME '{INDEX_NAME}' not found")
        
    except Exception as e:
        print(f"Error: {str(e)}")

    # try:
    #     search_indexer_client = SearchIndexerClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))
    #     existing_data_sources = search_indexer_client.get_data_source_connection_names()
        
    #     if DATA_SOURCE_CONNECTION_NAME in existing_data_sources:
    #         print(f"Data source '{DATA_SOURCE_CONNECTION_NAME}' exists. Deleting it...")
    #         search_indexer_client.delete_data_source_connection(DATA_SOURCE_CONNECTION_NAME)
    #         print(f"Data source '{DATA_SOURCE_CONNECTION_NAME}' deleted successfully!")
    #     else:
    #         print(f"Data source '{DATA_SOURCE_CONNECTION_NAME}' does not exist. ")

    # except Exception as e:
    #     print(f"Error deleting resources: {str(e)}")

    

    # try:
    #     search_indexer_client = SearchIndexerClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))
    #     existing_indexers = search_indexer_client.get_indexer_names()
    #     if INDEXER_NAME in existing_indexers:
    #         print("Existing indexer 'pdf-indexer' found. ")
    #         search_indexer_client.delete_indexer("pdf-indexer")
    #         print("Existing indexer 'pdf-indexer' deleted.")
    #     else:
    #         print(f"INDEXER NAME '{INDEXER_NAME}' not found")
        

    except Exception as e:
        print(f"Error: {str(e)}")




INDEX_SCHEMA = {
  "name": INDEX_NAME,
  "fields" :[
    SearchField(name="chunk_id", type=SearchFieldDataType.String, key=True, searchable=False, filterable=True, sortable=True),
    SearchField(name="chunk", type=SearchFieldDataType.String, searchable=True, filterable=False, sortable=False),
    SearchField(name="file_name", type=SearchFieldDataType.String, searchable=True, filterable=True, sortable=True)
]
}


def create_index():
    search_index_client = SearchIndexClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))
    index = SearchIndex(**INDEX_SCHEMA)
    search_index_client.create_index(index)
    print(f"Index '{INDEX_NAME}' created successfully!")
    
  


def create_data_source():       
        search_indexer_client = SearchIndexerClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))

        BLOB_NAME = "pdf-storage"  
        data_source_connection = SearchIndexerDataSourceConnection(
            name=DATA_SOURCE_CONNECTION_NAME,
            type="azureblob",  
            connection_string=BLOB_STORAGE_CONNECTION_STRING,  
            container={"name": BLOB_NAME}, 
            description="Blob container with PDF chunks"
        )
        search_indexer_client.create_data_source_connection(data_source_connection)
        print("Data source created successfully!")


def verify_data_source_connection():
    # Create a SearchIndexerClient
    search_indexer_client = SearchIndexerClient(
        endpoint=SEARCH_SERVICE_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_ADMIN_KEY)
    )

    try:
        # Retrieve data source connection details
        data_source = search_indexer_client.get_data_source_connection(DATA_SOURCE_CONNECTION_NAME)
        print(f"Data Source Connection '{DATA_SOURCE_CONNECTION_NAME}' found:")
        print(f"Name: {data_source.name}")
        print(f"Type: {data_source.type}")
        print(f"Connection String: {data_source.connection_string}")
        # data_source.container
        print(f"Container Name: {data_source.container}")
        print(f"Description: {data_source.description}")
    except Exception as e:
        print(f"Error: {e}")

# Call the verification function
# verify_data_source_connection()

# create_data_source()


def create_indexer():
        search_indexer_client = SearchIndexerClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))       
        indexer = SearchIndexer(
            name=INDEXER_NAME,
            data_source_name=DATA_SOURCE_CONNECTION_NAME,
            target_index_name=INDEX_NAME
        )
        search_indexer_client.create_indexer(indexer)
        print("Indexer 'pdf-indexer' created successfully!")
    
    
# create_indexer()






def check_indexer_status_and_run():
    try:
        search_indexer_client = SearchIndexerClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))
        indexer_name = INDEXER_NAME
        indexer_status = search_indexer_client.get_indexer_status(indexer_name)
    
        print(f"Indexer status: {indexer_status.status}")
        if indexer_status.status != "running":
            print(f"Indexer '{indexer_name}' is not running. Starting it now...")
            search_indexer_client.run_indexer(indexer_name)
            print("Indexer is running now...")
        else:
            print(f"Indexer '{indexer_name}' is already running. No action needed.")
            # reset_indexer()
    
    except Exception as e:
        print(f"Error checking or running the indexer: {str(e)}")

# check_indexer_status_and_run()
                                             


def reset_indexer():
    try:
        
        search_indexer_client = SearchIndexerClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))
        indexer_name = INDEXER_NAME
        search_indexer_client.reset_indexer(indexer_name)
        print(f"Indexer {indexer_name} has been reset successfully!")
    except Exception as e:
        print(f"Error resetting indexer: {str(e)}")

def count_documents():
    search_client = SearchClient(endpoint=SEARCH_SERVICE_ENDPOINT, index_name=INDEX_NAME, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))
    stats = search_client.get_document_count()
    print(f"Total documents in index '{INDEX_NAME}': {stats}")
# reset_indexer()
# count_documents()

def entire_flow():
    delete_existing_resources()
    create_index()
    # create_data_source()
    # create_indexer()
    # check_indexer_status_and_run()
    # count_documents()



# entire_flow()
