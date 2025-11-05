from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    for event in body["events"]:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_msg = event["message"]["text"]

            # OpenAI呼び出し（あいまいバスター）
            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": """
あなたは「あいまいバスター」として、ユーザーの文章から曖昧な表現（例：「いい感じ」「なるはや」「たぶん」「いつか」「多めに」「それ」「これ」など）をすべて特定し、論理的・客観的・誰でも理解できる明確な言葉に置き換える専門家です。主語が抜けている場合も補完してください。

文章が送られてきた場合は、以下に沿って添削を行ってください。

🧩 明確化バスター結果：

🔹 翻訳（あいまいバスターVer.）：
（明確化した文）

🔹 補足情報：
トーン：会話の温度感を記載（例：怒っている、急いでほしい、ゆっくりでいい　等）
目的：文章を書いた目的を記載（例：断る、指示を実行してほしい　等）
                            """,
                        },
                        {"role": "user", "content": user_msg},
                    ],
                },
            )
            reply_text = res.json()["choices"][0]["message"]["content"]

            # LINEへ返信
            requests.post(
                "https://api.line.me/v2/bot/message/reply",
                headers={"Authorization": f"Bearer {LINE_ACCESS_TOKEN}"},
                json={
                    "replyToken": event["replyToken"],
                    "messages": [{"type": "text", "text": reply_text}],
                },
            )
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
