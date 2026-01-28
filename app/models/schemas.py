from pydantic import BaseModel
from typing import Optional


class Prompt(BaseModel):
    prompt: str
    model: Optional[str] = None 
