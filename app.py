from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import gspread
import json
import tempfile
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])



google_credentials = os.getenv('GOOGLE_CREDENTIALS')
creds_json = json.loads(google_credentials)

# Write credentials to a temporary file
with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
    temp_file.write(json.dumps(creds_json).encode('utf-8'))
    temp_file_path = temp_file.name



# Google Sheets credentials
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(temp_file_path, scope)
client = gspread.authorize(creds)
#creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret_373873467094-09gahap4i6mcjuhapoeam50ikqts6tj9.apps.googleusercontent.com.json', scope)
#client = gspread.authorize(creds)



# Open the Google Sheet
spreadsheet = client.open("Car Rental Records")
sheet = spreadsheet.sheet1



@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
