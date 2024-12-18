# bot.py
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from chatbot import PDFChatBot

APP_ID = "Your-App-ID"
APP_PASSWORD = "Your-App-Password"

# Initialize adapter
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

bot = PDFChatBot()

async def on_turn(turn_context: TurnContext):
    await bot.on_turn(turn_context)

# Webhook server for receiving requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/messages", methods=["POST"])
def messages():
    if request.method == "POST":
        body = request.json
        activity = Activity().deserialize(body)
        turn_context = TurnContext(adapter, activity)
        return on_turn(turn_context)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
