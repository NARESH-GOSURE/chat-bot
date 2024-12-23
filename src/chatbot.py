import requests
import io
from werkzeug.datastructures import FileStorage
from botbuilder.core import ActivityHandler, TurnContext
from .cognitive_search import advanced_search
from .processing import upload_and_process_pdf_content
import json
import os
import enum
import datetime
from botbuilder.schema import Activity, ActivityTypes, ChannelAccount
uploaded_pdf_file_name = None

class PDFChatBot(ActivityHandler):
    def __init__(self, conversation_state, user_state):
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.uploaded_file_name = None
        self.transcript_property = []

    async def on_message_activity(self, turn_context: TurnContext):
        user_message = turn_context.activity.text
        # print("___tc------",turn_context.activity)
        self.transcript_property.append(turn_context.activity)

        if user_message == "hi":
            text_response="Hello! I am Procurity ChatBot. How can I assist you today?"
            await turn_context.send_activity(text_response)
            bot_response = self.bot_content(turn_context,text_response)
            self.transcript_property.append(bot_response)

        elif user_message == "bye":
            text_response="Goodbye! Have a great day!"
            bot_response = self.bot_content(turn_context, text_response)
            await turn_context.send_activity(text_response)
            self.transcript_property.append(bot_response)

        
        elif  user_message == 'upload':
            text_response="Please upload the PDF file as an attachment."
            await turn_context.send_activity(text_response)
            bot_response = self.bot_content(turn_context, text_response)
            self.transcript_property.append(bot_response)

        
        elif user_message == 'filename':
            if self.uploaded_file_name:
                text_response=f"Current File Name: {self.uploaded_file_name}"
                await turn_context.send_activity(text_response)
                bot_response = self.bot_content(turn_context, text_response)
                self.transcript_property.append(bot_response)   
            else:
                text_response="No file has been uploaded yet."
                await turn_context.send_activity(text_response)
                bot_response = self.bot_content(turn_context,text_response)
                self.transcript_property.append(bot_response)

        
        elif user_message == "search":
            if not self.uploaded_file_name:
                text_response="No file has been uploaded yet. Please upload a PDF first."
                await turn_context.send_activity(text_response)
                bot_response = self.bot_content(turn_context, text_response)
                self.transcript_property.append(bot_response)
            text_response="What is your query for the uploaded document?"
            await turn_context.send_activity(text_response)
            bot_response = self.bot_content(turn_context, text_response)
            self.transcript_property.append(bot_response)

        elif not user_message and  turn_context.activity.attachments:
            bot_responses= await self.handle_pdf_upload(turn_context)


        elif user_message.strip().endswith('?'):
            if self.uploaded_file_name:
                question = user_message.strip()
                response = advanced_search(question,self.uploaded_file_name)
                # print(response)
                final_response = await self.format_response(response)
                await turn_context.send_activity(final_response)
                bot_response = self.bot_content(turn_context, final_response)
                self.transcript_property.append(bot_response)
            else:
                text_response='Please add a pdf file'
                await turn_context.send_activity(text_response)
                bot_response = self.bot_content(turn_context, text_response)
                self.transcript_property.append(bot_response)
            
        elif user_message.strip().endswith('pdf'):
            query, file_name = await self.extract_query_and_filename(user_message)
            if file_name:
                response = advanced_search(query, file_name)
                final_response = await self.format_response(response)
                await turn_context.send_activity(final_response)
                bot_response = self.bot_content(turn_context, final_response)
                self.transcript_property.append(bot_response)
            else:
                text_response='The specified file name does not match the uploaded file.'
                await turn_context.send_activity(text_response)
                bot_response = self.bot_content(turn_context, text_response)
                self.transcript_property.append(bot_response)

        elif  user_message == "#save":
            print("Transcript Property List:")
            # for item in self.transcript_property:
            #     print(item)
            text_response="Transcript saved successfully!"
            await self.save_transcript(self.transcript_property)
            await turn_context.send_activity(text_response)
             
        else:
            text_response="I can help you upload a PDF or search its contents. Try typing 'upload' or 'search'."
            await turn_context.send_activity(text_response)
            bot_response = self.bot_content(turn_context, text_response)
            self.transcript_property.append(bot_response)


    async def handle_pdf_upload(self, turn_context: TurnContext):
        attachment = turn_context.activity.attachments[0]
        file_url = attachment.content_url
        file_name = attachment.name

        self.uploaded_file_name = file_name
        await self.download_file_and_upload_to_azure(file_url,file_name)
        await turn_context.send_activity(f"{file_name}  PDF uploaded successfully! You can now ask me questions about it.")

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
    
    async def save_transcript(self, history):
        history_dicts = [activity.serialize() for activity in history]
        transcript_json = json.dumps(history_dicts, indent=4)
        save_path = f"C:/transcripts/trans.transcript"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as file:
            file.write(transcript_json)
        

    def bot_content(self,turn_context,text_response):
        full_activity = turn_context.activity.create_reply(text_response)
        return full_activity
    

    def extract_values(self, activity):
        activity_dict = vars(activity) if hasattr(activity, '__dict__') else activity.__dict__
        for key, value in activity_dict.items():
            if isinstance(value, enum.Enum):  
                activity_dict[key] = value.name  
            elif isinstance(value, datetime.datetime):  
                activity_dict[key] = value.isoformat()  
            elif hasattr(value, '__dict__'):  
                activity_dict[key] = self.extract_values(value)
        json_data = json.dumps(activity_dict, default=str, indent=4)
        return activity_dict


