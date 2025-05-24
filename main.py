from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate
import random
import sqlite3
import os

app = Flask(__name__)

# LINEのアクセストークンとシークレットを環境変数から取得
line_bot_api = LineBotApi(os.environ.get("k3JMwXluTcuuYQH4q/qbLCETCTLaOzNnpzFGl621cmEiIMEHqQKX4WY8NZTWkkHkRyPUZsnt8Lv9Zr0Qy68oINOV3Im7LYYU5QYxES7V4vTSn80yFssDt/5LcuMjsLTUYUlgM6UjSlA9JfDT555QOQdB04t89/1O/w1cDnyilFU="))
handler = WebhookHandler(os.environ.get("81b94e611ef7f636b0d47752d798ca8d"))

# 四柱推命ロジック
def shichu_suimei(birth_date):
    # 四柱推命のアルゴリズム（簡単なサンプル）
    return f"四柱推命の結果: {birth_date}"

# タロットロジック
def tarot_reading():
    # タロットカードのランダム選択
    cards = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor"]
    selected_card = random.choice(cards)
    return f"タロットカード: {selected_card}"

# 数秘術ロジック
def numerology(birth_date):
    # 数秘術の簡単なアルゴリズム（サンプル）
    return f"数秘術の結果: {birth_date}"

# 西洋占星術ロジック
def astrology(birth_date):
    # 星座占いのサンプル
    return f"西洋占星術の結果: {birth_date}"

# メッセージのハンドリング
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.lower()

    # 「占い」のメッセージが来た場合にボタンを表示
    if "占い" in user_text:
        buttons_template = ButtonsTemplate(
            title="占いの種類を選んでください",
            text="占いたい種類を選んでください",
            actions=[
                {"type": "message", "label": "四柱推命", "text": "四柱推命"},
                {"type": "message", "label": "タロット", "text": "タロット"},
                {"type": "message", "label": "数秘術", "text": "数秘術"},
                {"type": "message", "label": "西洋占星術", "text": "占星術"},
            ]
        )
        # ボタンを送信
        line_bot_api.reply_message(event.reply_token, TemplateSendMessage(alt_text="占いの種類", template=buttons_template))

    # ボタンの選択に応じて占い結果を返す
    elif "四柱推命" in user_text:
        result = shichu_suimei("1990-05-15")  # 仮の生年月日
    elif "タロット" in user_text:
        result = tarot_reading()
    elif "数秘術" in user_text:
        result = numerology("1990-05-15")  # 仮の生年月日
    elif "占星術" in user_text:
        result = astrology("1990-05-15")  # 仮の生年月日
    else:
        result = "占いの種類を指定してください。"

    # 結果をLINEに返信
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))


# Webhookエンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
        abort(400)

    return 'OK'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
