from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import gspread
import tempfile
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])


# 从环境变量读取Google Sheets的认证信息
google_sheet_credentials = os.environ['GOOGLE_SHEET_CREDENTIALS']    #os.getenv('GOOGLE_SHEET_CREDENTIALS')
with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
    temp_file.write(google_sheet_credentials.encode('utf-8'))
    temp_file_path = temp_file.name



# Google Sheets credentials
scope = ["https://spreadsheets.google.com/feeds"]  #, "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(temp_file_path, scope)
#creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret_373873467094-09gahap4i6mcjuhapoeam50ikqts6tj9.apps.googleusercontent.com.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheet
spreadsheet = client.open("car_2024")
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
    text = event.message.text

    if text.startswith('借車'):
        date = text.split()[1]
        sheet.append_row([date])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"已紀錄借車日期: {date}")
        )
    elif text == '查詢借車記錄':
        records = sheet.get_all_records()
        reply_text = "\n".join([f"借車日期: {record['借車日期']}" for record in records])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text or "目前沒有借車記錄")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入 '借車 YYYY/MM/DD' 或 '查詢借車記錄'")
        )

if __name__ == "__main__":
    app.run(port=8000)
