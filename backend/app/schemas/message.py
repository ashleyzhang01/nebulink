from pydantic import BaseModel
from typing import Optional, List

class GeneralMessageSchema(BaseModel):
    message: str