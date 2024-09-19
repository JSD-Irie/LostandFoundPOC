import os
from azure.cosmos import CosmosClient, PartitionKey

# 環境変数から Cosmos DB の接続情報を取得
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = "MaterializedViewsDB"
LOST_ITEMS_CONTAINER_NAME = "LostItems"
LOST_ITEM_BY_SUBCATEGORY_CONTAINER_NAME = "LostItemsBySubcategory"

# Cosmos DB クライアントの初期化
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.create_database_if_not_exists(id=DATABASE_NAME)

# LostItems コンテナ
lost_items_container = database.create_container_if_not_exists(
    id=LOST_ITEMS_CONTAINER_NAME,
    partition_key=PartitionKey(path="/Municipality"),
    offer_throughput=400
)

# LostItemBySubcategory コンテナ
lost_item_by_subcategory_container = database.create_container_if_not_exists(
    id=LOST_ITEM_BY_SUBCATEGORY_CONTAINER_NAME,
    partition_key=PartitionKey(path="/Subcategory"),
    offer_throughput=400
)

def get_lost_item_container():
    """LostItems コンテナを返す"""
    return lost_items_container

def get_lost_item_by_subcategory_container():
    """LostItemBySubcategory コンテナを返す"""
    return lost_item_by_subcategory_container
