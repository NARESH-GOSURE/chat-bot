import asyncio
from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext, ConversationState, UserState, MemoryStorage
from botbuilder.schema import Activity
from src.chatbot import PDFChatBot 
from src.config import APP_ID,APP_PASSWORD
from botframework.connector import ConnectorClient
from botframework.connector.auth import MicrosoftAppCredentials
import logging

# # Define your Bot Framework App ID and Password
# APP_ID = "8b9b5962-a422-40c4-9b0e-de200eaad667"
# APP_PASSWORD = "c.q8Q~6OkyG4R~D5Hnuwkn15IpDTxZfL3-1VMc0E"

if APP_ID and APP_PASSWORD:
    adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
else:
    adapter_settings = BotFrameworkAdapterSettings(app_id=None, app_password=None)

SERVICE_URL='http://127.0.0.1:3978/api/messages'
adapter = BotFrameworkAdapter(adapter_settings)

# credentials = MicrosoftAppCredentials(APP_ID, APP_PASSWORD)
# connector_client = ConnectorClient(credentials, base_url=SERVICE_URL)
memory = MemoryStorage()
conversation_state = ConversationState(memory)
user_state = UserState(memory)


bot = PDFChatBot(conversation_state,user_state)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/api/messages", methods=["POST"])

async def messages():
    body = request.json
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")
    response = await adapter.process_activity(activity,auth_header, bot.on_turn)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=3978)
