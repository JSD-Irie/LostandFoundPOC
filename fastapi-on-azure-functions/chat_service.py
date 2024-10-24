import os
from openai import AzureOpenAI
from fastapi import UploadFile
import base64
from typing import Dict, List, Optional
from table_storage import list_lost_items
import logging
import json
from fastapi.encoders import jsonable_encoder


# Azure OpenAIのエンドポイントとAPIキーを環境変数から取得
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    async def process_image(self, image: UploadFile) -> Dict:
        try:
            # 画像をバイナリデータとして非同期に読み込む
            contents = await image.read()
            
            # 画像データをBase64エンコーディング
            encoded_image = base64.b64encode(contents).decode('utf-8')
            
            # data URIスキームに従ってフォーマットする
            image_data_uri = f"data:{image.content_type};base64,{encoded_image}"

            # キーワードの一覧を取得
            keywords = await self.get_keywords()
            if not keywords:
                return {"tags": [], "message": "キーワードが登録されていません。"}

            # キーワード一覧をカンマ区切りの文字列に変換
            keywords_str = ', '.join(keywords)

            # プロンプトの作成
            prompt = f"""
あなたは画像の内容を分析し、以下の情報をJSON形式で抽出するアシスタントです。

1. 画像から **color**（以下のリストから選択）を抽出してください。
   - 選択肢: ['black', 'red', 'blue', 'green', 'yellow', 'white', 'gray', 'brown', 'purple', 'pink', 'orange']

2. 画像から **itemName**（以下のリストから選択）を抽出してください。
   - 選択肢: ['手提げかばん', '財布', '傘', '時計', 'メガネ', '携帯電話', 'カメラ', '鍵', '本', 'アクセサリー', '携帯音響品']

3. 画像の特徴に応じて、以下のキーワード一覧から最も合致する1〜3つのタグを **tags** として選択してください。
   - キーワード一覧: {keywords_str}
   - 該当するキーワードがない場合は、空の配列を返してください。

レスポンスのJSON形式:
{{
    "color": "colorの値",
    "itemName": "itemNameの値",
    "tags": ["タグ1", "タグ2", "タグ3"]
}}

画像を分析して、上記の情報を抽出してください。
"""

            # メッセージリストを作成
            messages = [
                {
                    "role": "system",
                    "content": "あなたは画像の内容を分析し、指定された情報を抽出するアシスタントです。"
                },
                {
                    "role": "user",
                    "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{encoded_image}"}
                    }
                ]}
            ]

            # Azure OpenAIにリクエストを送信（同期メソッド）
            completion = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=messages,
                response_format= { "type":"json_object" },
            )

            # 応答のテキストを取得
            response_text = completion.choices[0].message.content.strip()
            logger.info(f"OpenAI response: {response_text}")

            # 応答をJSON形式に変換
            response_data = json.loads(response_text)

            # color、itemName、tagsを取得
            color = response_data.get("color", "")
            itemName = response_data.get("itemName", "")
            tags = response_data.get("tags", [])

            # tagsの数を確認し、0〜3個に制限
            if not isinstance(tags, list):
                tags = []
            tags = tags[:3]  # 最大3つまで

            result = {
                "color": color,
                "itemName": itemName,
                "tags": tags
            }

            # データをシリアライズ
            return jsonable_encoder(result)

        except Exception as e:
            logger.error(f"Failed to process image: {e}")
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
    
    async def get_keywords(self) -> List[str]:
        """
        キーワードの一覧を取得する関数
        """
        try:
            # Azure Table Storageから全アイテムを取得
            items = await list_lost_items()
            # 'keyword' フィールドを持つアイテムからキーワードを抽出し、重複を除外
            keywords = list({item["keyword"] for item in items if "keyword" in item})
            logger.info(f"Retrieved {len(keywords)} keywords.")
            return keywords
        except Exception as e:
            logger.error(f"Failed to get keywords: {e}")
            return []

    async def select_closest_keyword(self, free_text: str) -> str:
        """
        フリーワードからキーワードリスト内で最も近いものを選択して返す関数
        :param free_text: ユーザーからのフリーワード入力
        :return: 最も近いキーワード
        """
        try:
            # キーワードの一覧を取得
            keywords = await self.get_keywords()
            if not keywords:
                return "キーワードが見つかりませんでした。"

            # キーワード一覧をカンマ区切りの文字列に変換
            keywords_str = ', '.join(keywords)

            # プロンプトの作成
            prompt = f"""
            ユーザーからフリーワードが入力されるので、以下のキーワードのリストから最も近いキーワードを1つ選んで返してください。
            キーワード一覧:
            {keywords_str}

            フリーワード: {free_text}

            レスポンスはキーワードのみを返してください。
            """

            # Azure OpenAI APIを使用してプロンプトを送信
            completion = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはユーザーの入力に最も適したキーワードをキーワード一覧から選択するアシスタントです。",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            # 応答のキーワードを取得
            response_text = completion.choices[0].message.content.strip()
            logger.info(f"Selected keyword: {response_text}")
            return response_text
        except Exception as e:
            logger.error(f"Failed to select closest keyword: {e}")
            return f"エラーが発生しました: {str(e)}"