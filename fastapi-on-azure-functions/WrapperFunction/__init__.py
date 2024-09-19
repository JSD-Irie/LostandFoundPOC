from fastapi import FastAPI, HTTPException
import uuid
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import LostItem, LostItemBySubcategory
from database import get_lost_item_container, get_lost_item_by_subcategory_container
from chat_service import ChatService

class LostItemRequest(BaseModel):
    municipality: str
    subcategory: str
    description: Optional[str] = None
    contact: Optional[str] = None

app = FastAPI()

# Cosmos DB のコンテナ取得
lost_items_container = get_lost_item_container()  # LostItems コンテナ
lost_items_by_subcategory_container = get_lost_item_by_subcategory_container()  # LostItemBySubcategory コンテナ

@app.get("/lostitems", response_model=List[LostItem])
# 引数をNoneでもよいようにOptional型にしている
async def get_lost_items(municipality: Optional[str] = None, subcategory: Optional[str] = None):
    """
    Cosmos DB から忘れ物データをクエリし、結果を返す
    - `municipality`: 市区町村でフィルタリング
    - `subcategory`: 中分類でフィルタリング
    """
    chat_service = ChatService()
    query = "SELECT * FROM c"
    filters = []

    if municipality:
        municipality = chat_service.select_location(municipality)
        filters.append(f"c.Municipality = '{municipality}'")

    if subcategory:
        subcategory = chat_service.select_category(subcategory)
        filters.append(f"c.Subcategory = '{subcategory}'")

    if filters:
        query += " WHERE " + " AND ".join(filters)

    # クエリ実行 (LostItems コンテナ)
    items = list(lost_items_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    if not items:

        return []

    return items

@app.get("/lostitems/subcategory", response_model=List[LostItemBySubcategory])
async def get_lost_items_by_subcategory(subcategory: str):
    """
    Cosmos DB の LostItemBySubcategory コンテナから、中分類ごとの忘れ物データをクエリし、結果を返す
    """
    chat_service = ChatService()
    subcategory = chat_service.select_category(subcategory)
    query = f"SELECT * FROM c WHERE c.Subcategory = '{subcategory}'"
    
    # クエリ実行 (LostItemBySubcategory コンテナ)
    items = list(lost_items_by_subcategory_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    if not items:
        raise HTTPException(status_code=404, detail=f"Lost items with subcategory '{subcategory}' not found")

    return items

@app.post("/chat")
async def chat_service(message: str):
    """
    Azure OpenAI の GPT-3 によるチャットサービス
    """
    chat_service = ChatService()
    response = chat_service.select_category(message)

    return {"response": response}


@app.post("/lostitems")
async def add_lost_item(item: LostItemRequest):
    """
    新しい忘れ物データを Cosmos DB に追加する
    - `municipality`: 市区町村
    - `subcategory`: 中分類
    - `description`: 説明（任意）
    - `contact`: 連絡先（任意）
    """
    try:
        # データ作成
        current_time = datetime.utcnow().isoformat()  # 現在のUTC時刻を取得
        lost_item_data = {
            "id": str(uuid.uuid4()),  # 一意のIDを生成
            "Municipality": item.municipality,
            "Subcategory": item.subcategory,
            "Description": item.description if item.description else "説明なし",
            "ContactInfo": item.contact if item.contact else "連絡先なし",
            "DateFound": current_time,  # データが追加された時間
        }

        # Cosmos DB にアイテムを追加
        lost_items_container.create_item(body=lost_item_data)
        
        return {"message": "アイテムが正常に追加されました", "data": lost_item_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"アイテムの追加に失敗しました: {str(e)}")


@app.put("/lostitems/{item_id}")
async def update_lost_item(item_id: str, item: LostItemRequest):
    """
    既存の忘れ物データを更新する
    - `item_id`: 更新するデータのID
    - `municipality`: 市区町村
    - `subcategory`: 中分類
    - `description`: 説明（任意）
    - `contact`: 連絡先（任意）
    """
    try:
        # 既存のアイテムを取得
        existing_item = lost_items_container.read_item(item=item_id, partition_key=item.municipality)

        # 更新データを反映
        existing_item["Municipality"] = item.municipality
        existing_item["Subcategory"] = item.subcategory
        existing_item["Description"] = item.description if item.description else existing_item["Description"]
        existing_item["ContactInfo"] = item.contact if item.contact else existing_item["ContactInfo"]
        existing_item["DateUpdated"] = datetime.utcnow().isoformat()  # 更新日時を追加

        # Cosmos DB に更新されたアイテムを保存
        lost_items_container.replace_item(item=existing_item, body=existing_item)

        return {"message": "アイテムが正常に更新されました", "data": existing_item}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"アイテムの更新に失敗しました: {str(e)}")