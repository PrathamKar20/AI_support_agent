# Query validation schema
from pydantic import BaseModel
class QueryRequest(BaseModel):
    query: str
