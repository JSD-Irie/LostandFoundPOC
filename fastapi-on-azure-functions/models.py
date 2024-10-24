# models.py
from pydantic import BaseModel, Extra
from typing import List, Optional
from datetime import datetime

class Item(BaseModel):
    categoryCode: Optional[str] = None
    categoryName: Optional[str] = None
    itemName: Optional[str] = None
    valuableFlg: Optional[int] = None

class JapaneseCurrency(BaseModel):
    count: int
    id: str

class Currency(BaseModel):
    foreignCurrency: Optional[str] = None
    japaneseCurrency: Optional[List[JapaneseCurrency]] = None

class Color(BaseModel):
    id: str
    name: str
    url: str

class Status(BaseModel):
    id: str
    name: str

class KeywordRequest(BaseModel):
    keyword: Optional[str] = None
    itemType: Optional[str] = None

class LostItemRequest(BaseModel):
    createUserPlace: Optional[str] = None          # 市区町村（オプショナル）
    findDateTime: Optional[datetime] = None        # 発見日時（オプショナル）
    memo: Optional[str] = None                     # メモ（オプショナル）
    contact: Optional[str] = None                  # 連絡先（オプショナル）
    color: Optional[Color] = None                   # カラー情報（オプショナル）
    createUserID: Optional[str] = None             # 作成ユーザーID（オプショナル）
    currency: Optional[Currency] = None            # 通貨情報（オプショナル）
    findPlace: Optional[str] = None                # 発見場所（オプショナル）
    imageUrl: List[str] = []                        # 画像URL（オプショナル）
    isValuables: Optional[bool] = None              # 貴重品かどうか（オプショナル）
    item: Optional[Item] = None                     # アイテム情報（オプショナル）
    keyword: List[str] = []                         # キーワード（オプショナル）
    mngmtNo: Optional[str] = None                    # 管理番号（オプショナル）
    personal: Optional[str] = None                   # 個人情報（オプショナル）
    status: Optional[Status] = None                 # ステータス（オプショナル）

    class Config:
        extra = Extra.allow  # 追加のフィールドを許可

class LostItem(LostItemRequest):
    id: str
    item: Optional[Item] = None  # 明示的にオプショナルに定義

    class Config:
        extra = Extra.allow

class KeywordUpdateRequest(BaseModel):
    keyword: List[str] = []  # キーワードリスト

class LostItemBySubcategory(LostItemRequest):
    id: str
    item: Optional[Item] = None  # 明示的にオプショナルに定義

    class Config:
        extra = Extra.allow

class isCheckedUpdateRequest(BaseModel):
    isChecked: bool