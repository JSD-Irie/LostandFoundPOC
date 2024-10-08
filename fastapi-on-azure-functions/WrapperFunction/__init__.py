# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
import uuid
from datetime import datetime, timedelta
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
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import os

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

chat_service = ChatService()

# Cosmos DB のコンテナ取得
lost_items_container = get_lost_item_container()  # LostItems コンテナ
lost_items_by_subcategory_container = get_lost_item_by_subcategory_container()  # LostItemBySubcategory コンテナ

# 環境変数から設定を取得
BLOB_CONTAINER_NAME = "images"  # コンテナ名
BLOB_ACCOUNT_URL = os.getenv("AZURE_BLOB_ACCOUNT_URL")  # ストレージアカウントのURL

@app.get("/lostitems", response_model=List[LostItem])
async def get_lost_items(municipality: Optional[str] = None, categoryName: Optional[str] = None, color: Optional[str] = None, findDate: Optional[str] = None):
    """
    Cosmos DB から忘れ物データをクエリし、結果を返す
    - `municipality`: 市区町村でフィルタリング
    - `categoryName`: 中分類でフィルタリング
    - `color`: 色でフィルタリング
    - `findDate`: 指定日数以内でフィルタリング
    """
    query = "SELECT * FROM c"
    filters = []

    if municipality:
        municipality = chat_service.select_location(municipality)
        filters.append(f"c.createUserPlace = '{municipality}'")

    if categoryName:
        categoryName = chat_service.select_category(categoryName)
        filters.append(f"c.item.categoryName = '{categoryName}'")

    if color:
        filters.append(f"c.color.id = '{color}'")

    # 日付フィルタ
    if findDate:
        today = datetime.utcnow()
        if findDate == 'today':
            filters.append(f"c.findDateTime >= '{today.strftime('%Y-%m-%dT%H:%M:%S')}'")
        elif findDate == 'yesterday':
            yesterday = today - timedelta(days=1)
            filters.append(f"c.findDateTime >= '{yesterday.strftime('%Y-%m-%dT%H:%M:%S')}'")
        elif findDate == 'last_week':
            last_week = today - timedelta(weeks=1)
            filters.append(f"c.findDateTime >= '{last_week.strftime('%Y-%m-%dT%H:%M:%S')}'")
        elif findDate == 'last_month':
            last_month = today - timedelta(weeks=4)  # 1ヶ月を4週間とする
            filters.append(f"c.findDateTime >= '{last_month.strftime('%Y-%m-%dT%H:%M:%S')}'")

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

@app.delete("/lostitems/{id}", response_model=LostItem)
async def delete_lost_item(id: str):
    """
    指定されたIDを持つ忘れ物データを削除する
    :param id: 削除する忘れ物データのID
    :return: 削除された忘れ物データ
    """
    query = f"SELECT * FROM c WHERE c.id = '{id}'"
    logger.info(f"Executing query: {query}")

    try:
        items = list(lost_items_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        if not items:
            raise HTTPException(status_code=404, detail="アイテムが見つかりません")

        item_to_delete = items[0]
        partition_key = item_to_delete['createUserPlace']  # 実際のパーティションキーのフィールド名に置き換えてください

        # アイテムを削除
        lost_items_container.delete_item(item=item_to_delete['id'], partition_key=partition_key)
        logger.info(f"Deleted lost item with ID: {id}")

        # Pydanticモデルに変換して返す
        deleted_item = LostItem(**item_to_delete)
        return deleted_item

    except Exception as e:
        logger.error(f"Failed to delete lost item: {e}")
        raise HTTPException(status_code=500, detail=f"アイテムの削除に失敗しました: {str(e)}")

@app.post("/imagescan")
async def scan_image(image: UploadFile = File(...)):
    """
    画像をアップロードし、処理を行うエンドポイント
    :param image: アップロードされた画像ファイル
    :return: 処理結果
    """    
    try:
        result = chat_service.process_image(image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"画像の処理に失敗しました: {str(e)}")

@app.post("/upload-image")
async def upload_image(image: UploadFile = File(...)):
    """
    画像をAzure Blob Storageにアップロードするエンドポイント
    :param image: アップロードされた画像ファイル
    :return: アップロードした画像のURL
    """
    try:
        # DefaultAzureCredentialを使ったBlobServiceClientの初期化
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=BLOB_ACCOUNT_URL, credential=credential)
        # Blobのクライアントを作成
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=image.filename)
        
        # 画像をアップロード
        blob_client.upload_blob(image.file.read(), overwrite=True)
        
        # アップロードした画像のURLを生成
        image_url = f"{BLOB_ACCOUNT_URL}/{BLOB_CONTAINER_NAME}/{image.filename}"
        
        return {"imageUrl": image_url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"画像のアップロードに失敗しました: {str(e)}")