from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from models import (
    LostItem,
    LostItemBySubcategory,
    KeywordRequest,
    LostItemRequest,
    Currency,
    JapaneseCurrency,
    Color,
    Status,
    Item,
    KeywordUpdateRequest
)
from database import get_lost_item_container, get_lost_item_by_subcategory_container
from chat_service import ChatService
import logging
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import os
from table_storage import add_lost_item as add_lost_item_to_table_storage, list_lost_items  # 修正
import asyncio
import concurrent.futures
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry, ImageFileCreateBatch
from msrest.authentication import CognitiveServicesCredentials
from msrest.authentication import ApiKeyCredentials

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
AZURE_TABLE_ENDPOINT = os.getenv("AZURE_TABLE_ENDPOINT")  # 追加
CUSTOM_VISION_ENDPOINT = os.getenv('CUSTOM_VISION_ENDPOINT')
CUSTOM_VISION_PROJECT_ID = os.getenv('CUSTOM_VISION_PROJECT_ID')
CUSTOM_VISION_TRAINING_KEY = os.getenv('CUSTOM_VISION_TRAINING_KEY')

# DefaultAzureCredential の初期化
credential = ApiKeyCredentials(in_headers={"Training-key": CUSTOM_VISION_TRAINING_KEY})

# Custom Vision Training クライアントの初期化
trainer = CustomVisionTrainingClient(
    endpoint=CUSTOM_VISION_ENDPOINT,
    credentials=credential
)

executor = concurrent.futures.ThreadPoolExecutor()

@app.get("/lostitems", response_model=List[LostItem])
async def get_lost_items(
    free_text: Optional[str] = None,
    municipality: Optional[str] = None,
    itemName: Optional[str] = None,
    color: Optional[str] = None,
    findDate: Optional[str] = None
):
    """
    Cosmos DB から忘れ物データをクエリし、結果を返す
    - `free_text`: フリーワードで検索
    - `municipality`: 市区町村でフィルタリング
    - `itemName`: 中分類でフィルタリング
    - `color`: 色でフィルタリング
    - `findDate`: 指定日数以内でフィルタリング
    """
    query = "SELECT * FROM c"
    filters = []
    parameters = []

    # フリーワードから最も近いキーワードを取得
    if free_text:
        keyword = await chat_service.select_closest_keyword(free_text)
        filters.append("ARRAY_CONTAINS(c.keyword, @keyword)")
        parameters.append({"name": "@keyword", "value": keyword})

    if municipality:
        municipality_selected = chat_service.select_location(municipality)
        filters.append("c.createUserPlace = @municipality")
        parameters.append({"name": "@municipality", "value": municipality_selected})

    if itemName:
        itemName_selected = chat_service.select_category(itemName)
        filters.append("c.item.itemName = @itemName")
        parameters.append({"name": "@itemName", "value": itemName_selected})

    if color:
        filters.append("c.color.id = @color")
        parameters.append({"name": "@color", "value": color})

    # 日付フィルタ
    if findDate:
        today = datetime.utcnow()
        if findDate == 'today':
            date_value = today.strftime('%Y-%m-%dT00:00:00')
        elif findDate == 'yesterday':
            date_value = (today - timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
        elif findDate == 'last_week':
            date_value = (today - timedelta(weeks=1)).strftime('%Y-%m-%dT00:00:00')
        elif findDate == 'last_month':
            date_value = (today - timedelta(weeks=4)).strftime('%Y-%m-%dT00:00:00')
        else:
            date_value = None

        if date_value:
            filters.append("c.findDateTime >= @findDate")
            parameters.append({"name": "@findDate", "value": date_value})

    if filters:
        query += " WHERE " + " AND ".join(filters)

    logger.info(f"Executing query: {query} with parameters {parameters}")

    try:
        items = list(lost_items_container.query_items(
            query=query,
            parameters=parameters,
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
        lost_item_data["isChecked"] = False

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

# 既存のアイテムを更新するエンドポイント
@app.put("/lostitems/{id}/keywords", response_model=LostItem)
async def update_keywords(id: str, update_request: KeywordUpdateRequest):
    """
    指定されたIDの忘れ物データのキーワードを更新する
    :param id: 更新する忘れ物データのID
    :param update_request: 更新するキーワードのリスト
    :return: 更新された忘れ物データ
    """
    try:
        # アイテムを取得
        query = f"SELECT * FROM c WHERE c.id = '{id}'"
        items = list(lost_items_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        if not items:
            raise HTTPException(status_code=404, detail="アイテムが見つかりません")

        # 最初の一致するアイテムを取得
        item_to_update = items[0]
        partition_key = item_to_update['createUserPlace']

        # キーワードを更新
        item_to_update['keyword'] = update_request.keyword
        item_to_update['isChecked'] = True

        # 更新をDBに反映
        lost_items_container.replace_item(item=item_to_update['id'], body=item_to_update)

        # Pydanticモデルに変換して返す
        updated_item = LostItem(**item_to_update)
        return updated_item

    except Exception as e:
        logger.error(f"Failed to update keywords for item with ID {id}: {e}")
        raise HTTPException(status_code=500, detail=f"キーワードの更新に失敗しました: {str(e)}")
    

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

# 登録されているすべての遺失物を削除するエンドポイント
@app.delete("/lostitems")
async def delete_all_lost_items():
    """
    登録されているすべての遺失物を削除するエンドポイント
    """
    try:
        # Cosmos DB からすべてのアイテムを取得
        items = list(lost_items_container.read_all_items())

        # すべてのアイテムを削除
        for item in items:
            partition_key = item['createUserPlace']  # 実際のパーティションキーのフィールド名に置き換えてください
            lost_items_container.delete_item(item=item['id'], partition_key=partition_key)
            logger.info(f"Deleted lost item with ID: {item['id']}")

        return {"message": "Deleted all lost items"}

    except Exception as e:
        logger.error(f"Failed to delete all lost items: {e}")
        raise HTTPException(status_code=500, detail=f"アイテムの削除に失敗しました: {str(e)}")

@app.post("/imagescan")
async def scan_image(image: UploadFile = File(...)):
    """
    画像をアップロードし、処理を行うエンドポイント
    :param image: アップロードされた画像ファイル
    :return: 処理結果
    """    
    try:
        result = await chat_service.process_image(image)
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
executor = concurrent.futures.ThreadPoolExecutor()


@app.post("/azure-lostitems", response_model=dict)
async def add_azure_lost_item(item: KeywordRequest):
    """
    新しい遺失物データを Azure Table Storage に追加するエンドポイント
    """
    try:
        logger.info(f"Adding lost item to Azure Table Storage: {item}")

        # データ準備
        lost_item_data = item.dict()
        lost_item_data["DateFound"] = datetime.utcnow().isoformat()

        # Azure Table Storageに追加（非同期で実行）
        added_item = await add_lost_item_to_table_storage(lost_item_data)

        logger.info(f"Added lost item with RowKey: {added_item['RowKey']}")
        return added_item

    except Exception as e:
        logger.error(f"Failed to add lost item to Azure Table Storage: {e}")
        raise HTTPException(status_code=500, detail=f"アイテムの追加に失敗しました: {str(e)}")

# 新しいエンドポイント：Azure Table Storageから遺失物を一覧取得
@app.get("/azure-lostitems", response_model=List[str])
async def get_azure_lost_items(
    item_type: Optional[str] = None,
    color: Optional[str] = None,
    find_date: Optional[str] = None
):
    """
    Azure Table Storage から遺失物データを一覧取得するエンドポイント
    - `item_type`: アイテムの種類でフィルタリング
    - `color`: 色でフィルタリング
    - `find_date`: 指定日数以内でフィルタリング（today, yesterday, last_week, last_month）
    """
    try:
        filters = {}
        if item_type:
            filters["ItemType"] = item_type
        if color:
            filters["Color"] = color
        if find_date:
            filters["findDate"] = find_date

        # Azure Table Storageからデータを取得（非同期で実行）
        items = await list_lost_items(filters)

        # keywordフィールドのみを抽出し、重複を除いたリストを作成
        keywords = list({item["keyword"] for item in items if "keyword" in item})

        return keywords

    except Exception as e:
        logger.error(f"Failed to retrieve lost items: {e}")
        raise HTTPException(status_code=500, detail=f"データの取得に失敗しました: {str(e)}")

@app.post("/select-keyword")
async def select_keyword(free_text: str):
    """
    フリーワードから最も近いキーワードを取得するエンドポイント
    :param free_text: ユーザーからのフリーワード入力
    :return: 最も近いキーワード
    """
    try:
        keyword = await chat_service.select_closest_keyword(free_text)
        return {"keyword": keyword}
    except Exception as e:
        logger.error(f"Failed to select keyword: {e}")
        raise HTTPException(status_code=500, detail=f"キーワードの選択に失敗しました: {str(e)}")

@app.post("/label-image")
async def label_image(
    label_names: List[str] = Form(...),
    image: UploadFile = File(...)
):
    try:
        # プロジェクトの取得
        project = trainer.get_project(CUSTOM_VISION_PROJECT_ID)
        if not project:
            raise HTTPException(status_code=404, detail="プロジェクトが見つかりません。")
        
        # ラベルの存在確認と取得
        existing_tags = trainer.get_tags(CUSTOM_VISION_PROJECT_ID)
        tags_to_add = []
        for label_name in label_names:
            tag = next((t for t in existing_tags if t.name.lower() == label_name.lower()), None)
            if not tag:
                tag = trainer.create_tag(CUSTOM_VISION_PROJECT_ID, label_name)
                if not tag:
                    raise HTTPException(status_code=500, detail=f"ラベル '{label_name}' の作成に失敗しました。")
            tags_to_add.append(tag.id)
        
        if not tags_to_add:
            raise HTTPException(status_code=400, detail="有効なラベルが指定されていません。")
        
        # 画像の読み込み
        image_data = await image.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="画像データが空です。")
        
        # 画像エントリの作成
        image_entry = ImageFileCreateEntry(
            name=image.filename,
            contents=image_data,
            tag_ids=tags_to_add
        )
        
        # バッチの作成
        batch = ImageFileCreateBatch(images=[image_entry])
        
        # 画像のアップロードとラベル付け
        results = trainer.create_images_from_files(CUSTOM_VISION_PROJECT_ID, batch)

        logger.info(f"画像のラベル付け結果: {results}")
        
        if not results.is_batch_successful:
            errors = []
            for image_result in results.images:
                if image_result.status != "OK" and image_result.status != "OKDuplicate":
                    errors.append({
                        "image": image_result.image.id if image_result.image else "不明な画像",
                        "status": image_result.status
                    })
            return JSONResponse(status_code=400, content={"errors": errors})
        
        return {"message": "画像が正常にラベル付けされました。"}
    
    except HTTPException as he:
        logger.error(f"HTTPエラーが発生しました: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="サーバー内部でエラーが発生しました。")