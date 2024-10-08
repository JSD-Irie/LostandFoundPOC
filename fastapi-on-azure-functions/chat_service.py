import os
from openai import AzureOpenAI
from fastapi import UploadFile
import base64
from typing import Dict


# Azure OpenAIのエンドポイントとAPIキーを環境変数から取得
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

class ChatService:
    def __init__(self):
        # Azure OpenAIのクライアントを作成
        self.client = AzureOpenAI(
            api_version="2023-07-01-preview",
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )

    def select_category(self, message: str) -> str:
        try:
            # GPTに対して最も近い選択肢を探すプロンプト
            prompt = """
            ユーザーから言葉が入力されるので選択肢から最も近い言葉を1つ選んで返してください。
            選択肢にない場合でも、**選択肢の中から**最も近いものを選んでください。

            # 選択肢
            - 手提げかばん
            - 財布
            - 傘
            - 時計
            - メガネ
            - 携帯電話
            - カメラ
            - 鍵
            - 本
            - アクセサリー
            - 携帯音響品

            # 例
            ## Input
            グラサン
            ## Output
            メガネ
            
            ## Input
            スマホ
            ## Output
            携帯電話

            ## Input
            ウォッチ
            ## Output
            時計

            ## Input
            教科書
            ## Output
            本
            """

            # Azure OpenAI APIを使用してプロンプトを送信
            completion = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,  # デプロイ名（例: gpt-35-turbo）
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
            )

            # 応答の文章のみを取得
            response_text = completion.choices[0].message.content.strip()
            print(f"Response: {response_text}")
            return response_text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def select_location(self, message: str) -> str:
        try:
            # GPTに対して最も近い選択肢を探すプロンプト
            prompt = """
            ユーザーから言葉が入力されるので選択肢から最も近い言葉を1つ選んで返してください。
            選択肢にない場合でも、**選択肢の中から**最も近いものを選んでください。

            # 選択肢
            - 旭川市
            - 函館市
            - 小樽市
            - 千歳市
            - 苫小牧市
            - 室蘭市
            - 北見市
            - 札幌駅

            # 例
            ## Input
            北見
            ## Output
            北見市
            
            ## Input
            しろいし
            ## Output
            札幌市白石区

            ## Input
            札幌
            ## Output
            札幌駅

            ## Input
            ちとせ
            ## Output
            千歳市
            """

            # Azure OpenAI APIを使用してプロンプトを送信
            completion = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,  # デプロイ名（例: gpt-35-turbo）
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
            )

            # 応答の文章のみを取得
            response_text = completion.choices[0].message.content.strip()
            print(f"Response: {response_text}")
            return response_text
        except Exception as e:
            return f"Error: {str(e)}"

    def process_image(self, image: UploadFile) -> Dict:
        """
        画像ファイルを処理し、特徴をJSON形式で返す関数
        :param image: アップロードされた画像ファイル
        :return: 特徴を含むJSONデータ
        """
        PROMPT_TEMPLATE = """
        与えられた画像を分析して、JSON形式で情報を抽出してください。レスポンスは以下の構造に従ってください。

        {
            "color": "以下のリストから選んでください: ['black', 'red', 'blue', 'green', 'yellow', 'white', 'gray', 'brown', 'purple', 'pink', 'orange']",
            "categoryName": "以下のリストから該当するカテゴリを選んでください: ['手提げかばん', '財布', '傘', '時計', 'メガネ', '携帯電話', 'カメラ', '鍵', '本', 'アクセサリー']",
            "memo": "画像内の物の特徴を100文字以内で簡潔に説明してください。"
        }

        ### 例:

        例1:
        画像の説明: 金色のジッパーがついた小さな赤い財布。
        レスポンス:
        {
            "color": "red",
            "categoryName": "財布",
            "memo": "小さな赤い財布で、金色のジッパーがついています。"
        }

        例2:
        画像の説明: 木製の曲がった取っ手がついた黒色の傘。
        レスポンス:
        {
            "color": "black",
            "categoryName": "傘",
            "memo": "黒色の傘で、曲がった木製の取っ手があります。"
        }

        では、画像を分析し、上記の構造に基づいてJSON形式で回答してください。
        """
        try:
            # 画像をバイナリデータとして読み込む
            contents = image.file.read()
            
            # 画像データをBase64エンコーディング
            encoded_image = base64.b64encode(contents).decode('utf-8')
            
            # data URIスキームに従ってフォーマットする
            image_url = f"data:{image.content_type};base64,{encoded_image}"
            
            # メッセージリストを作成
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": PROMPT_TEMPLATE
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]

            # Azure OpenAIにリクエストを送信
            response = self.send_request_to_azure_openai(messages)

            # response_textをJSON形式に変換して返す
            return self.format_response_to_json(response['message'])
        except Exception as e:
            return {"error": str(e)}

    def send_request_to_azure_openai(self, messages):
        """
        Azure OpenAIにリクエストを送信し、レスポンスを取得する関数
        :param messages: メッセージリスト
        :return: OpenAIからのレスポンス
        """
        try:
            completion = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,  # デプロイ名（例: gpt-35-turbo）
                messages=messages
            )
            response_text = completion.choices[0].message.content.strip()
            return {"message": response_text}
        except Exception as e:
            return {"error": str(e)}

    def format_response_to_json(self, response_text: str) -> Dict:
        """
        APIのレスポンスをJSON形式に変換する関数
        :param response_text: APIからのレスポンステキスト
        :return: JSON形式の辞書
        """
        # ここでレスポンステキストをJSON形式に変換するロジックを実装
        import json

        # ここでは単純にJSON形式に変換することを想定しています
        # ただし、実際のレスポンス内容によっては適切にパースする必要があります
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"error":  response_text}