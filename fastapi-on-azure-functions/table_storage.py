# table_storage.py

from azure.data.tables import TableServiceClient, TableClient, UpdateMode
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from typing import Optional
import os
import uuid
from datetime import datetime, timedelta
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数からテーブルストレージのエンドポイントを取得
TABLE_ENDPOINT = os.getenv("AZURE_TABLE_ENDPOINT")  # 例: https://<your-storage-account>.table.core.windows.net/
TABLE_NAME = "LostItems"

# DefaultAzureCredentialを使用してTableServiceClientを初期化
credential = DefaultAzureCredential()
table_service_client = TableServiceClient(endpoint=TABLE_ENDPOINT, credential=credential)

async def get_table_client():
    try:
        table_client = table_service_client.get_table_client(table_name=TABLE_NAME)
        # テーブルが存在しない場合は作成
        table_client.create_table()
        logger.info(f"Table '{TABLE_NAME}' is ready.")
        return table_client
    except ResourceExistsError:
        logger.info(f"Table '{TABLE_NAME}' already exists.")
        return table_service_client.get_table_client(table_name=TABLE_NAME)
    except Exception as e:
        logger.error(f"Failed to create or get table '{TABLE_NAME}': {e}")
        raise


async def add_lost_item(data: dict) -> dict:
    """
    Azure Table Storageに遺失物データを追加する関数
    :param data: 遺失物データの辞書
    :return: 追加されたデータの辞書
    """
    try:
        # 一意のRowKeyを生成（UUIDを使用）
        row_key = str(uuid.uuid4())
        partition_key = data.get("itemType", "Unknown")

        # タイムスタンプの設定
        timestamp = datetime.utcnow().isoformat()

        entity = {
            "PartitionKey": partition_key,
            "RowKey": row_key,
            "Timestamp": timestamp,
            **data
        }

        logger.info(f"Adding lost item with RowKey: {entity}")

        # テーブルクライアントの取得を非同期に実行
        table_client = await get_table_client()

        table_client.create_entity(entity=entity)
        logger.info(f"Added lost item with RowKey: {row_key}")
        return entity

    except ResourceExistsError:
        logger.error("Entity already exists.")
        raise
    except Exception as e:
        logger.error(f"Failed to add lost item: {e}")
        raise

async def list_lost_items(filters: Optional[dict] = None) -> list:
    """
    Azure Table Storageから遺失物データを一覧取得する関数
    :param filters: フィルタリング条件の辞書
    :return: 遺失物データのリスト
    """
    try:
        table_client = await get_table_client()
        query_filter = ""
        if filters:
            filter_clauses = []
            for key, value in filters.items():
                if key == "findDate":
                    # 日付フィルタはISO形式に変換
                    if value == 'today':
                        date = datetime.utcnow().date()
                        filter_clauses.append(f"LostDateTime ge '{date.isoformat()}'")
                    elif value == 'yesterday':
                        date = datetime.utcnow().date() - timedelta(days=1)
                        filter_clauses.append(f"LostDateTime ge '{date.isoformat()}'")
                    elif value == 'last_week':
                        date = datetime.utcnow().date() - timedelta(weeks=1)
                        filter_clauses.append(f"LostDateTime ge '{date.isoformat()}'")
                    elif value == 'last_month':
                        date = datetime.utcnow().date() - timedelta(weeks=4)
                        filter_clauses.append(f"LostDateTime ge '{date.isoformat()}'")
                elif key == "keyword":
                    # キーワードフィルタ
                    filter_clauses.append(f"keyword eq '{value}'")
                else:
                    filter_clauses.append(f"{key} eq '{value}'")
            query_filter = " and ".join(filter_clauses)

        if query_filter:
            entities = table_client.query_entities(query_filter)
        else:
            entities = table_client.list_entities()

        items = [dict(entity) for entity in entities]
        logger.info(f"Retrieved {len(items)} items from Azure Table Storage.")
        return items

    except Exception as e:
        logger.error(f"Failed to list lost items: {e}")
        raise

async def delete_all_labels():
    """
    Azure Table Storage内の全ての遺失物データを削除する関数
    """
    try:
        table_client = await get_table_client()
        entities = table_client.list_entities()
        for entity in entities:
            table_client.delete_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])
        logger.info("All lost items have been deleted.")
    except Exception as e:
        logger.error(f"Failed to delete all lost items: {e}")
        raise

async def delete_lost_items_by_keyword(keyword: str):
    """
    指定されたキーワードを持つ遺失物データを削除する関数
    :param keyword: 削除対象のキーワード
    """
    try:
        table_client = await get_table_client()

        # キーワードに一致するエンティティをクエリ
        filter_query = f"keyword eq '{keyword}'"
        entities = table_client.query_entities(filter_query)

        deleted_count = 0
        for entity in entities:
            partition_key = entity['PartitionKey']
            row_key = entity['RowKey']
            table_client.delete_entity(partition_key=partition_key, row_key=row_key)
            logger.info(f"Deleted entity with PartitionKey: {partition_key}, RowKey: {row_key}")
            deleted_count += 1

        logger.info(f"Deleted {deleted_count} items with keyword '{keyword}'")
    except Exception as e:
        logger.error(f"Failed to delete items with keyword '{keyword}': {e}")
        raise
