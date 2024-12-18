from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
import requests

class PDFChatBot(ActivityHandler):
    def __init__(self):
        # Store the file name after a PDF is uploaded
        self.file_name = None

    async def on_message_activity(self, turn_context: TurnContext):
        user_input = turn_context.activity.text.strip()

        # If the user wants to upload a PDF, handle that first
        if "upload pdf" in user_input.lower():
            await turn_context.send_activity("Please upload the PDF file.")
            # Here, you can handle file upload logic in your backend system.
        
        elif self.file_name and "search" in user_input.lower():
            # If the file has already been uploaded, use the file name for search
            query = self.extract_query(user_input)
            if query:
                await self.handle_search(turn_context, query)
            else:
                await turn_context.send_activity("Please provide a valid search query.")
        elif "search" in user_input.lower():
            # If no file has been uploaded, ask for file name and query
            await turn_context.send_activity("Please upload a PDF first before searching.")
        
        else:
            # General response when the user asks for help or other queries
            await turn_context.send_activity("I can help you upload a PDF or search its contents. Try 'upload pdf' or 'search'.")
    
    async def handle_search(self, turn_context: TurnContext, query: str):
        # If a file is uploaded, use it for the search
        if self.file_name:
            response = self.search_in_pdf(query, self.file_name)
            await turn_context.send_activity(f"Search results: {response}")
        else:
            await turn_context.send_activity("No PDF uploaded. Please upload a PDF first.")
    
    def extract_query(self, user_input):
        # Extract the search query from user input (for simplicity, assume user sends the full query)
        return user_input.replace("search", "").strip()

    def search_in_pdf(self, query, file_name):
        # Make an API call to Flask for advanced search using the file name and query
        api_url = "http://your-flask-backend-url/advanced-search"
        headers = {'x-api-key': 'your-api-key'}
        params = {'query': query, 'file_name': file_name}
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()  # Return search result
        else:
            return "Error in searching the PDF."

    # Method to simulate PDF upload for the purpose of this example
    async def handle_pdf_upload(self, file_name: str):
        # This method would be triggered when a PDF is uploaded via the backend
        self.file_name = file_name
        return f"File '{file_name}' uploaded successfully and ready for searching."

