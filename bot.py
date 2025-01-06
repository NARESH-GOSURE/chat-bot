import asyncio
from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, ConversationState, UserState, MemoryStorage
from botbuilder.schema import Activity
from sqlalchemy import null
from src.chatbot import PDFChatBot 
from src.config import APP_ID,APP_PASSWORD
from botframework.connector import ConnectorClient
from botframework.connector.auth import MicrosoftAppCredentials
import logging
import os
import json
from datetime import datetime
from storage import save_conversation


if APP_ID and APP_PASSWORD:
    adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
else:
    adapter_settings = BotFrameworkAdapterSettings(app_id=None, app_password=None)

SERVICE_URL='http://127.0.0.1:3978/api/messages'
adapter = BotFrameworkAdapter(adapter_settings)

memory = MemoryStorage()
conversation_state = ConversationState(memory)
user_state = UserState(memory)

# CONVERSATION_LOG = "conversation_log.json"

def save_conversation_to_mongo(user_id, activity):
    jobtypename="Chatbot"
    input_activity = {
        "timestamp": activity.timestamp.isoformat() if isinstance(activity.timestamp, datetime) else activity.timestamp,
        "text": None if activity.text == null  else activity.text,
        "type": activity.type,
        "role": activity.from_property.role
    }
    save_conversation(jobtypename,user_id,input_activity)


bot = PDFChatBot(conversation_state,user_state)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/api/messages", methods=["POST"])

async def messages():
    body = request.json
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")
    save_conversation_to_mongo(activity.from_property.id, activity)
    response_activity = await adapter.process_activity(activity,auth_header, bot.on_turn)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
