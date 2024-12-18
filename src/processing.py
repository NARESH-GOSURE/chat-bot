from .document_intelligence import extract_pdf_and_store_chunks_in_blob
from .upload_to_index import upload_to_index
from .blob_storage import upload

def upload_and_process_pdf_content(file):
    pdf_name =upload(file)
    print("Document Analysis Started")
    pdf_chunks_name= extract_pdf_and_store_chunks_in_blob(pdf_name)
    upload_to_index(pdf_chunks_name)
    return pdf_name


