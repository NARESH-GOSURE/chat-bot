from flask import Flask, request, jsonify, Blueprint
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, ContentFormat
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from .config import PDF_STORAGE_CONTAINER_NAME
from .config import AZURE_ENDPOINT,AZURE_KEY
from .blob_storage import get_pdf_from_blob,upload_chunks_to_azure_blob
from .config import AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, LLM_MODEL
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

def document_analysis_from_url(form_url):
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=AZURE_ENDPOINT, credential=AzureKeyCredential(AZURE_KEY)
    )
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-read",
        
        AnalyzeDocumentRequest(url_source=form_url),
        output_content_format=ContentFormat.MARKDOWN,
    )
    result = poller.result()


    text_content = ""
    for page in result.pages:
        for line in page.lines:
            text_content += line.content + "\n"
    return text_content



def analyze_pdf(pdf_path):
    from azure.ai.documentintelligence.models import AnalyzeOutputOption, AnalyzeResult
    document_intelligence_client = DocumentIntelligenceClient(endpoint=AZURE_ENDPOINT, credential=AzureKeyCredential(AZURE_KEY))
    # with open(pdf_path, "rb") as file:
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-read",
        analyze_request=pdf_path,
        output=[AnalyzeOutputOption.PDF],
        content_type="application/octet-stream",
    )
    result: AnalyzeResult = poller.result()
    # operation_id = poller.details["operation_id"]
    # response = document_intelligence_client.get_analyze_result_pdf(model_id=result.model_id, result_id=operation_id)
    # with open("analyze_result.pdf", "wb") as writer:
    #     writer.writelines(response)
                
    text_content = ""
    for page in result.pages:
        for line in page.lines:
            text_content += line.content + "\n"
            # print(result.pages)
    return text_content



def text_chunking_with_overlaping(text, pdf_file_name,chunk_size=800, overlap_size=150):
    chunks = []
    start = 0
    chunk_id = 1 
    renamed_pdf_file_name  = pdf_file_name.replace(" ", "_")
    new_pdf_file_name = renamed_pdf_file_name.replace('.', '_') 
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if overlap_size > 0 and end + overlap_size < len(text):
            next_chunk = text[end:end + overlap_size]
            chunk += next_chunk

        chunk_unique_id = f"{new_pdf_file_name}_chunk_{chunk_id}"     
        chunks.append({"chunk_id": chunk_unique_id, "chunk": chunk,"file_name":pdf_file_name})
        chunk_id += 1
        start = end
    
    return chunks


class DocumentClassificationResponse(BaseModel):
    document_type: str = Field(description="The classified type of the document (Technical Specifications, Pricing Templates, Evaluation Criteria, FAR Proposal Documents, or Other)")

def get_pdf_document_type(pdf_content: str):
    parser = PydanticOutputParser(pydantic_object=DocumentClassificationResponse)
    client = AzureOpenAI(
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=f"{AZURE_OPENAI_ENDPOINT}?api-version={AZURE_OPENAI_API_VERSION}",
        api_key=AZURE_OPENAI_API_KEY
    )

    template = """
    You are an AI document classifier. Analyze the following PDF content and classify it into one of the categories below based on the content and structure:

    Categories:
    1. Technical Specifications
    2. Pricing Templates
    3. Evaluation Criteria
    4. FAR Proposal Documents

    If the document does not fit any of these categories, classify it as "Other".

    ### PDF Content:
    {pdf_content}

    ### Instructions:
    - Return the document type from the list.
    - If the document does not clearly match any category, return 'Other' and briefly explain why.

    ### Classification:
    {format_instructions}
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["pdf_content"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    formatted_prompt = prompt.format(pdf_content=pdf_content)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": formatted_prompt}
        ],
        model=LLM_MODEL,
    )
    
    if chat_completion.choices:
        parsed_output = parser.invoke(chat_completion.choices[0].message.content)
        return parsed_output.document_type

def extract_pdf_and_store_chunks_in_blob(PDF_FILE_NAME):
    pdf_data = get_pdf_from_blob(PDF_STORAGE_CONTAINER_NAME, PDF_FILE_NAME)
    extracted_content_pdf = analyze_pdf(pdf_data)
    document_type = get_pdf_document_type(extracted_content_pdf)
    # print(document_type)
    pdf_chunks_output = text_chunking_with_overlaping(extracted_content_pdf,PDF_FILE_NAME)
    chunk_blob_storage_name = upload_chunks_to_azure_blob(pdf_chunks_output,PDF_FILE_NAME)
    return chunk_blob_storage_name

