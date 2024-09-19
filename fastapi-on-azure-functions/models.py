from pydantic import BaseModel
from datetime import datetime

class LostItem(BaseModel):
    id: str
    Municipality: str
    Subcategory: str
    DateFound: datetime
    Description: str
    ContactInfo: str

class LostItemBySubcategory(BaseModel):
    id: str
    Subcategory: str
    Municipality: str
    DateFound: datetime
    Description: str
    ContactInfo: str
