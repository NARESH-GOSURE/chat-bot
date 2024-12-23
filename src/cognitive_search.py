from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from .config import SEARCH_ADMIN_KEY, SEARCH_SERVICE_ENDPOINT,SEARCH_SERVICE_ENDPOINT,PDF_INDEX_NAME
from .llm import llm_response_generation

search_client = SearchClient(endpoint=SEARCH_SERVICE_ENDPOINT, index_name=PDF_INDEX_NAME, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))

def advanced_search(query_text,file_name,top=5):
    search_filter = None
    if file_name:
        search_filter = f"file_name eq '{file_name}'"  
        results = search_client.search(search_text=query_text, top=top, filter=search_filter)
        if results:
            return llm_response_generation(search_results=results,question=query_text)
        else:
            return "No results found for the given query."





























# # Search the index
# def search_query(query):
#     results = search_client.search(query)
#     res = list(results)
#     # print(list(results))
#     print(res)
#     # for i in res:
#     #     print(i['content'])

    
#     if not results:
#         print(f"No results found for the query: '{query}'")
#         return

#     for result in res:
#         print(f"Document ID: {result['id']}")
#         print(f"Content: {result['content']}")
#         print("----------")

# Perform a search query
# search_query("possibility")
































































# def count_documents():
#     stats = search_client.get_document_count()
#     print(f"Total documents in index '{PDF_INDEX_NAME}': {stats}")

# count_documents()






# def search_document_by_id(doc_id):
#     try:
#         # Perform the search with a filter on the document ID
#         results = search_client.search("*", filter=f"id eq '{doc_id}'")
#         print(results)
#         for result in results:
#             print(f"Document found: {result['id']} - {result['content']}")
#         return results

#     except Exception as e:
#         print(f"Error searching for document by ID: {str(e)}")
#         return None

# # Check if document is indexed (by querying its ID)
# def verify_document_indexing(doc_id):
#     print(f"Checking if document with ID '{doc_id}' is indexed...")
#     results = search_document_by_id(doc_id)
#     if results:
#         print(f"Document {doc_id} is indexed.")
#     else:
#         print(f"Document {doc_id} not found in the index.")

# Verify total document count in index
# count_documents()

# Replace with a specific document ID you want to check
doc_id_to_check = "page-7-offset-13666"  # Replace with your actual document ID
# verify_document_indexing(doc_id_to_check)


# a = search_client.index_documents(index_name)
# print(a)




