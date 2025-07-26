import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# --- Flaskアプリケーションの初期化 ---
app = Flask(__name__)

# --- Gemini APIキーの設定 ---
# ⚠️重要：ここにあなたのGemini APIキーを貼り付けてください。
genai.configure(api_key="AIzaSyDH6yANBFtUeUhKxR2iYPOmvG-4nSA1Xto")

# --- 知識ベース（カンペ）を読み込む関数 ---
def load_knowledge_base(restaurant_id):
    try:
        with open(f'knowledge_{restaurant_id}.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

# --- AIに送るプロンプト（命令書）を作成する関数 ---
def create_prompt(knowledge_base, question):
    return f"""
# 命令書
あなたは、以下の「知識ベース」の情報だけを元に回答する、レストランの優秀なAIアシスタントです。
# 厳格なルール
1.  回答は、必ず「知識ベース」内の情報のみを使用してください。
2.  知識ベースにない質問には、「申し訳ありませんが、その情報については分かりかねます。お店に直接お問い合わせください。」と正直に回答してください。
3.  フレンドリーかつ丁寧な言葉遣いを徹底してください。
---
# 知識ベース
{knowledge_base}
---
# お客様からの質問
{question}
# 回答
"""

# --- トップページ（チャット画面）を表示するためのルート ---
@app.route('/')
def index():
    return render_template('index.html')

# --- チャットの質問を受け取り、AIの回答を返すためのAPIルート ---
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    restaurant_id = "restaurant_101"

    if not question:
        return jsonify({"error": "質問が空です。"}), 400

    knowledge_base = load_knowledge_base(restaurant_id)
    if not knowledge_base:
        return jsonify({"error": "レストラン情報が見つかりません。"}), 404

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = create_prompt(knowledge_base, question)
    response = model.generate_content(prompt)

    return jsonify({"answer": response.text})

# --- このファイルが直接実行されたときにサーバーを起動 ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)
