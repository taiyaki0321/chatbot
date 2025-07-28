import os
from dotenv import load_dotenv # これが重要です！
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# --- 1. 環境変数を読み込む ---
load_dotenv() # この行が、.envファイルを読み込む命令です！

# --- 2. Gemini APIキーの設定とAIモデルの初期化 ---
api_key = os.getenv('GOOGLE_API_KEY') # .envファイルから 'GOOGLE_API_KEY' の値を取得

if not api_key:
    # APIキーが読み込めなかった場合のエラーメッセージ
    raise ValueError("GOOGLE_API_KEY 環境変数が設定されていません。または値が空です。") 
    
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')



# --- Flaskアプリケーションの初期化 ---
app = Flask(__name__)

# --- 知識ベース（カンペ）を読み込む関数 ---
def load_knowledge_base(restaurant_id):
    """
    指定されたレストランIDに基づいて知識ベースファイルを読み込む。
    """
    try:
        # knowledge_restaurant_101.txt のようなファイル名を想定
        with open(f'knowledge_{restaurant_id}.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"エラー: knowledge_{restaurant_id}.txt が見つかりません。")
        return None
    except Exception as e:
        print(f"知識ベースの読み込み中にエラーが発生しました: {e}")
        return None

# --- AIに送るプロンプト（命令書）を作成する関数 ---
def create_prompt(knowledge_base, question):
    """
    Geminiモデルに送るプロンプトを生成する。
    """
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
    """
    チャット画面のHTMLテンプレートを表示する。
    """
    return render_template('index.html')

# --- チャットの質問を受け取り、AIの回答を返すためのAPIルート ---
@app.route('/ask', methods=['POST'])
def ask():
    """
    ユーザーからの質問を受け取り、Geminiモデルで回答を生成して返す。
    """
    data = request.json
    question = data.get('question')
    
    # ここではrestaurant_idを固定していますが、
    # 複数のレストランを扱う場合は、リクエストから取得するなど動的にする必要があります。
    restaurant_id = "restaurant_101" 

    if not question:
        return jsonify({"error": "質問が空です。"}), 400

    knowledge_base = load_knowledge_base(restaurant_id)
    if not knowledge_base:
        return jsonify({"error": "レストラン情報が見つかりません。知識ベースを読み込めませんでした。"}), 500 # 404から500に変更

    print("1. 応答生成を開始します。")
    try:
        print("2. Google Gemini APIを呼び出しています...")
        
        # グローバルで初期化した model 変数を使用
        prompt = create_prompt(knowledge_base, question)
        response = model.generate_content(prompt) 
        
        print("3. Google Gemini APIから応答がありました！")
        
        # response.text でAIの生成したテキストを取得
        answer = response.text
        
        return jsonify({"answer": answer})

    except Exception as e:
        print(f"AI応答生成中にエラーが発生しました: {e}")
        return jsonify({"error": "申し訳ありませんが、AIの応答生成中にエラーが発生しました。お店に直接お問い合わせください。"}), 500

# --- このファイルが直接実行されたときにサーバーを起動 ---
if __name__ == '__main__':
    # デバッグモードを有効にし、ポート5001でサーバーを起動
    # 本番環境ではdebug=Falseに設定してください
    app.run(debug=True, port=5001)


