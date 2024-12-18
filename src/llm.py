from pydantic import BaseModel, Field
from typing import List
from openai import AzureOpenAI
import json
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from .config import AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, LLM_MODEL


class Result(BaseModel):
    question: str = Field(description="The question that was asked")
    answer: str = Field(description="Yes, No, or N/A")

class StructuredResponse(BaseModel):
    answer: str = Field(description="The structured response containing the question, answer, and context chunks")
    reason: str = Field(description="The reason for the answer, set empty string if the answer is N/A")

def generated_structured_output(pdf_content: str, question: str):
    parser = PydanticOutputParser(pydantic_object=StructuredResponse)
    client = AzureOpenAI(
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=f"{AZURE_OPENAI_ENDPOINT}?api-version={AZURE_OPENAI_API_VERSION}",
        api_key=AZURE_OPENAI_API_KEY
    )

    template = """
    You are a helpful chatbot assistant named **Procurity-Bot** designed to answer questions based on the content of a specific PDF document.

    ### Instructions:
    - Your answers should be based **only on the information provided** in the document.
    - If the document contains relevant information to answer the question, provide the answer in multiple lines.
    - If the document does not contain relevant information, respond with "N/A".
    - Do **not** make assumptions, fabricate information, or provide answers based on external knowledge.
.

    ### Context (Content from the PDF):
    {pdf_content}

    ### User's Question:
    {question}

    ### Answer:
    {format_instructions}
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["pdf_content", "question"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    prompt = prompt.format(pdf_content=pdf_content,question=question)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model=LLM_MODEL,
    )
    if(len(chat_completion.choices)):
        parsed_output = parser.invoke(chat_completion.choices[0].message.content)
        return parsed_output

    return StructuredResponse(
        answer="N/A",
        reason=""
    )


def process_search_results_and_generate_llm_structured_response(search_results, input_question: str):
    chunk_content =""
    for chunk in search_results:
        chunk_content = chunk_content+chunk['chunk']
    response = generated_structured_output(pdf_content=chunk_content,question=input_question)
    result = Result(
        question=input_question,
        answer=response.answer
    )
    return result

def convert_structure_response_to_json_format(structured_response):
  final_result_dict = {
      "question": structured_response.question,
      "answer": structured_response.answer
  }
#   json_output = json.dumps(final_result_dict, indent=4)
  return final_result_dict



def llm_response_generation(search_results, question: str):
    llm_structured_response = process_search_results_and_generate_llm_structured_response(search_results, question)
    final_response = convert_structure_response_to_json_format(llm_structured_response)
    return final_response


# print(llm_response_generation(search,"monopoly"))