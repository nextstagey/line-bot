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
    year, month, day = map(int, birth_date.split("-"))
    life_path_number = (year + month + day) % 9
    if life_path_number == 1:
        result = "あなたの運勢は「新しい始まり」を意味します。挑戦する時です！"
    elif life_path_number == 2:
        result = "協力や調和が大事な時期です。周りとの関係を大切にしましょう。"
    else:
        result = "良い運勢の時期に差し掛かっています。チャンスを逃さず行動して！"
    return f"四柱推命による占い結果です：\n{result}"

# タロットロジック
def tarot_reading():
    cards = {
        "The Fool": "新しい始まりや冒険を意味します。",
        "The Magician": "創造力と力強い意志を示します。",
        "The High Priestess": "直感や知識を重視する時期です。",
        "The Empress": "母性や育成の象徴。育てる力を持っています。",
        "The Emperor": "安定性、支配、管理を意味します。",
    }
    selected_card = random.choice(list(cards.keys()))
    card_meaning = cards[selected_card]
    return f"タロット占いの結果です：\nあなたの引いたカードは「{selected_card}」です。\nそのカードの意味は：{card_meaning}"

# 数秘術ロジック
def numerology(birth_date):
    numbers = [int(digit) for digit in str(birth_date).replace("-", "")]
    life_path_number = sum(numbers) % 9
    numerology_meanings = {
        1: "独立心とリーダーシップの象徴です。",
        2: "協調性と協力を大切にするタイプ。",
        3: "表現力豊かでクリエイティブ。",
        4: "堅実で実直な努力家。",
    }
    return f"数秘術占いの結果です：\nあなたのライフパスナンバーは「{life_path_number}」です。\nその意味は：{numerology_meanings.get(life_path_number, '他の数字の特徴です。')}"

# 西洋占星術ロジック
def astrology(birth_date):
    month = int(birth_date.split("-")[1])
    zodiac = ""
    if month in [3, 4, 5]:
        zodiac = "おひつじ座"
        result = f"西洋占星術による占い結果です：\nあなたの星座は「{zodiac}」です。\n今月は大きな変化が訪れます。前向きに挑戦して！"
    elif month in [6, 7, 8]:
        zodiac = "おうし座"
        result = f"あなたの星座は「{zodiac}」です。\n今月は安定した状況を求めるべき時期です。慎重に行動して！"
    else:
        zodiac = "ふたご座"
        result = f"あなたの星座は「{zodiac}」です。\n新しい人間関係の構築に力を入れましょう！"
    return result

# SQLiteデータベース接続
def connect_db():
    conn = sqlite3.connect('user_history.db')
    return conn

# ユーザー履歴を保存
def save_history(user_id, result):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS history (user_id TEXT, result TEXT)")
    cursor.execute("INSERT INTO history (user_id, result) VALUES (?, ?)", (user_id, result))
    conn.commit()
    conn.close()

# ユーザー履歴を取得
def get_history(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT result FROM history WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# メインのメッセージ処理
def handle_message(event):
    user_text = event.message.text.lower()

    # 「占い」メッセージが送られた場合、ボタンを表示
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
        # ここでボタンを送信
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
    save_history(event.source.user_id, result)  # 履歴保存
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
