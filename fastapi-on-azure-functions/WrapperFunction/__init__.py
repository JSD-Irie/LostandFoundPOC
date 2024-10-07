# main.py
from fastapi import FastAPI, HTTPException
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from models import (
    LostItem,
    LostItemBySubcategory,
    LostItemRequest,
    Currency,
    JapaneseCurrency,
    Color,
    Status,
    Item
)
from database import get_lost_item_container, get_lost_item_by_subcategory_container
from chat_service import ChatService
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Cosmos DB のコンテナ取得
lost_items_container = get_lost_item_container()  # LostItems コンテナ
lost_items_by_subcategory_container = get_lost_item_by_subcategory_container()  # LostItemBySubcategory コンテナ

@app.get("/lostitems", response_model=List[LostItem])
async def get_lost_items(municipality: Optional[str] = None, categoryName: Optional[str] = None):
    """
    Cosmos DB から忘れ物データをクエリし、結果を返す
    - `municipality`: 市区町村でフィルタリング
    - `categoryName`: 中分類でフィルタリング
    """
    chat_service = ChatService()
    query = "SELECT * FROM c"
    filters = []

    if municipality:
        municipality = chat_service.select_location(municipality)
        filters.append(f"c.createUserPlace = '{municipality}'")

    if categoryName:
        categoryName = chat_service.select_category(categoryName)
        filters.append(f"c.item.categoryName = '{categoryName}'")

    if filters:
        query += " WHERE " + " AND ".join(filters)

    logger.info(f"Executing query: {query}")

    try:
        items = list(lost_items_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        logger.info(f"Retrieved {len(items)} items from Cosmos DB")
    except Exception as e:
        logger.error(f"Failed to execute query: {e}")
        raise HTTPException(status_code=500, detail=f"データの取得に失敗しました: {str(e)}")

    if not items:
        return []

    # Pydanticモデルに変換
    try:
        return [LostItem(**item) for item in items]
    except Exception as e:
        logger.error(f"Failed to convert data to Pydantic models: {e}")
        raise HTTPException(status_code=500, detail=f"データの変換に失敗しました: {str(e)}")

@app.get("/lostitems/subcategory", response_model=List[LostItemBySubcategory])
async def get_lost_items_by_subcategory(subcategory: str):
    """
    Cosmos DB の LostItemBySubcategory コンテナから、中分類ごとの忘れ物データをクエリし、結果を返す
    """
    chat_service = ChatService()
    subcategory = chat_service.select_category(subcategory)
    query = f"SELECT * FROM c WHERE c.item.categoryName = '{subcategory}'"

    logger.info(f"Executing query: {query}")

    try:
        items = list(lost_items_by_subcategory_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        logger.info(f"Retrieved {len(items)} items for subcategory '{subcategory}'")
    except Exception as e:
        logger.error(f"Failed to execute query: {e}")
        raise HTTPException(status_code=500, detail=f"データの取得に失敗しました: {str(e)}")

    if not items:
        raise HTTPException(status_code=404, detail=f"Lost items with subcategory '{subcategory}' not found")

    # Pydanticモデルに変換
    try:
        return [LostItemBySubcategory(**item) for item in items]
    except Exception as e:
        logger.error(f"Failed to convert data to Pydantic models: {e}")
        raise HTTPException(status_code=500, detail=f"データの変換に失敗しました: {str(e)}")

@app.post("/lostitems", response_model=LostItem)
async def add_lost_item(item: LostItemRequest):
    """
    新しい忘れ物データを Cosmos DB に追加する
    """
    try:
        logger.info(f"Adding lost item: {item}")

        # データ作成
        current_time = datetime.utcnow()
        lost_item_data = item.dict()
        lost_item_data["id"] = str(uuid.uuid4())  # 一意のIDを生成
        lost_item_data["DateFound"] = current_time  # データが追加された時間

        # JSONシリアライズ可能な形式に変換
        lost_item_data_encoded = jsonable_encoder(lost_item_data)

        # Cosmos DB にアイテムを追加
        lost_items_container.create_item(body=lost_item_data_encoded)
        logger.info(f"Added lost item with ID: {lost_item_data['id']}")

        # Pydanticモデルに変換
        created_item = LostItem(**lost_item_data)

        return created_item

    except Exception as e:
        logger.error(f"Failed to add lost item: {e}")
        raise HTTPException(status_code=500, detail=f"アイテムの追加に失敗しました: {str(e)}")

@app.put("/lostitems/{item_id}", response_model=LostItem)
async def update_lost_item(item_id: str, item: LostItemRequest):
    """
    既存の忘れ物データを更新する
    """
    try:
        logger.info(f"Updating lost item with ID: {item_id} with data: {item}")

        # 既存のアイテムを取得
        existing_item = lost_items_container.read_item(item=item_id, partition_key=item.createUserPlace)
        logger.info(f"Retrieved existing item: {existing_item}")

        # 更新データを辞書に変換（未設定のフィールドを除外）
        update_data = item.dict(exclude_unset=True)
        update_data["DateUpdated"] = datetime.utcnow()  # 更新日時を追加

        # 更新されたフィールドのみを反映
        for key, value in update_data.items():
            existing_item[key] = value

        # JSONシリアライズ可能な形式に変換
        existing_item_encoded = jsonable_encoder(existing_item)

        # Cosmos DB に更新されたアイテムを保存
        lost_items_container.replace_item(item=existing_item, body=existing_item_encoded)
        logger.info(f"Updated lost item with ID: {item_id}")

        # Pydanticモデルに変換
        updated_item = LostItem(**existing_item)

        return updated_item

    except Exception as e:
        logger.error(f"Failed to update lost item: {e}")
        raise HTTPException(status_code=500, detail=f"アイテムの更新に失敗しました: {str(e)}")
