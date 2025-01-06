import requests
import io
from sqlalchemy import null
from werkzeug.datastructures import FileStorage
from botbuilder.core import ActivityHandler, TurnContext
from .cognitive_search import advanced_search
from .processing import upload_and_process_pdf_content
from storage import save_conversation
from datetime import datetime
from botbuilder.schema import Activity, ActivityTypes, ChannelAccount

uploaded_pdf_file_name = None

# CONVERSATION_LOG = "conversation_log.json"
def save_conversation_to_mongo(user_id, activity):
    jobtypename="Chatbot"
    input_activity = {
        "timestamp": activity.timestamp.isoformat() if isinstance(activity.timestamp, datetime) else activity.timestamp,
        "text": None if activity.text == null  else activity.text,
        "type": activity.type,
        "role": "bot"
    }
    save_conversation(jobtypename,user_id,input_activity)

class PDFChatBot(ActivityHandler):
    def __init__(self, conversation_state, user_state):
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.uploaded_file_name = None

    async def on_message_activity(self, turn_context: TurnContext):
        user_message = turn_context.activity.text

        if user_message == "hi":
            text_response="Hello! I am Procurity ChatBot. How can I assist you today?"
            
        elif user_message == "bye":
            text_response="Goodbye! Have a great day!"
            
        elif  user_message == 'upload':
            text_response="Please upload the PDF file as an attachment."
                    
        elif user_message == "search":
            if not self.uploaded_file_name:
                text_response="No file has been uploaded yet. Please upload a PDF first."
            else:
                text_response="What is your query for the uploaded document?"
                

        elif not user_message and  turn_context.activity.attachments:
            text_response= await self.handle_pdf_upload(turn_context)


        elif user_message.strip().endswith('?'):
            if self.uploaded_file_name:
                question = user_message.strip()
                response = advanced_search(question,self.uploaded_file_name)
                text_response = await self.format_response(response)
            else:
                text_response='Please add a pdf file'
                
            
        elif user_message.strip().endswith('pdf'):
            query, file_name = await self.extract_query_and_filename(user_message)
            if file_name:
                response = advanced_search(query, file_name)
                text_response = await self.format_response(response)
            else:
                text_response='The specified file name does not match the uploaded file.'
                
        else:
            text_response="I can help you upload a PDF or search its contents. Try typing 'upload' or 'search'."
        
        bot_activity = Activity(
            text=text_response,
            type="message",
            timestamp=datetime.utcnow()
        )

        save_conversation_to_mongo(turn_context.activity.from_property.id,bot_activity)
        await turn_context.send_activity(text_response)        



    async def handle_pdf_upload(self, turn_context: TurnContext):
        attachment = turn_context.activity.attachments[0]
        file_url = attachment.content_url
        file_name = attachment.name

        self.uploaded_file_name = file_name
        await self.download_file_and_upload_to_azure(file_url,file_name)
        text_response = f"{file_name}  PDF uploaded successfully! You can now ask me questions about it."
        return text_response

    async def download_file_and_upload_to_azure(self, file_url,file_name):
        response = requests.get(file_url)
        pdf_stream = io.BytesIO(response.content)
        file = FileStorage(pdf_stream, filename=file_name)                   
        uploaded_pdf_file_name = upload_and_process_pdf_content(file)

    async def format_response(self,response):
        answer = response.get('answer', 'No answer available.')
        if answer=="N/A":
            answer = 'No Matching content for input query'
        return answer
    
    async def extract_query_and_filename(self,user_message):
        question_index = user_message.rfind('?')
        if question_index != -1:
            query = user_message[:question_index + 1].strip()  
            file_name = user_message[question_index + 1:].strip()
            return query.strip(), file_name.strip()
        else:
            return user_message.strip(), None  
    


