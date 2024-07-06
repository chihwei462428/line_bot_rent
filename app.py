from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['dJNLKF+0PpiVz73YIUP/fq2gRmzlWH0Hii5RYaGGU1mIMh4TjJV6bFZuPDGf2X90j2Zxo0R3Ts2axD1EdPwXv/Kd4MRMYTpfwwha/9Y8EdFNJGna7o8Y/PVfxG7P52sfkupaknbEdha8qaHqSYUE7wdB04t89/1O/w1cDnyilFU='])
handler = WebhookHandler(os.environ['061db312aa8705bb3a069a42a5c11b93'])


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

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
