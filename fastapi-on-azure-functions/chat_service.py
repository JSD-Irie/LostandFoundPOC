import os
from openai import AzureOpenAI


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
            ユーザーから言葉が入力されるのでリストから最も近い言葉を1つ選んで返してください。
            リスト内にない場合でも最も近いものを選んでください。

            選択肢:
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

            # 例
            ユーザーの入力: グラサン
            回答: メガネ
            
            ユーザーの入力: スマホ
            回答: 携帯電話

            ユーザーの入力: ウォッチ
            回答: 時計

            ユーザーの入力: 教科書
            回答: 本
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
            ユーザーから言葉が入力されるのでリストから最も近い言葉を1つ選んで返してください。
            リスト内にない場合でも最も近いものを選んでください。

            選択肢:
            - 札幌市白石区
            - 札幌市中央区
            - 札幌市豊平区
            - 旭川市
            - 函館市
            - 小樽市
            - 千歳市
            - 苫小牧市
            - 室蘭市
            - 北見市

            # 例
            ユーザーの入力: 北見
            回答: 北見市
            
            ユーザーの入力: しろいし
            回答: 札幌市白石区

            ユーザーの入力: 札幌
            回答: 札幌市中央区

            ユーザーの入力: とよひら
            回答: 札幌市豊平区
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
