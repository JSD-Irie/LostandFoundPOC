from fastapi import FastAPI, HTTPException
from typing import List
from models import LostItem, LostItemBySubcategory
from database import get_lost_item_container, get_lost_item_by_subcategory_container

app = FastAPI()

# Cosmos DB のコンテナ取得
lost_items_container = get_lost_item_container()  # LostItems コンテナ
lost_items_by_subcategory_container = get_lost_item_by_subcategory_container()  # LostItemBySubcategory コンテナ

@app.get("/lostitems", response_model=List[LostItem])
async def get_lost_items(municipality: str = None, subcategory: str = None):
    """
    Cosmos DB から忘れ物データをクエリし、結果を返す
    - `municipality`: 市区町村でフィルタリング
    - `subcategory`: 中分類でフィルタリング
    """
    query = "SELECT * FROM c"
    filters = []

    if municipality:
        filters.append(f"c.Municipality = '{municipality}'")

    if subcategory:
        filters.append(f"c.Subcategory = '{subcategory}'")

    if filters:
        query += " WHERE " + " AND ".join(filters)

    # クエリ実行 (LostItems コンテナ)
    items = list(lost_items_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    if not items:
        raise HTTPException(status_code=404, detail="Lost items not found")

    return items

@app.get("/lostitems/subcategory", response_model=List[LostItemBySubcategory])
async def get_lost_items_by_subcategory(subcategory: str):
    """
    Cosmos DB の LostItemBySubcategory コンテナから、中分類ごとの忘れ物データをクエリし、結果を返す
    """
    query = f"SELECT * FROM c WHERE c.Subcategory = '{subcategory}'"
    
    # クエリ実行 (LostItemBySubcategory コンテナ)
    items = list(lost_items_by_subcategory_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    if not items:
        raise HTTPException(status_code=404, detail=f"Lost items with subcategory '{subcategory}' not found")

    return items
