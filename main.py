from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境変数からトークンとシークレットを取得
line_bot_api = LineBotApi(os.environ.get("k3JMwXluTcuuYQH4q/qbLCETCTLaOzNnpzFGl621cmEiIMEHqQKX4WY8NZTWkkHkRyPUZsnt8Lv9Zr0Qy68oINOV3Im7LYYU5QYxES7V4vTSn80yFssDt/5LcuMjsLTUYUlgM6UjSlA9JfDT555QOQdB04t89/1O/w1cDnyilFU="))
handler = WebhookHandler(os.environ.get("81b94e611ef7f636b0d47752d798ca8d"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    reply_text = f"占い結果🔮\nあなたが送った内容：{user_text}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()
