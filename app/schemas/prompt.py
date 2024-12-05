from pydantic import BaseModel

class Prompt(BaseModel):
    prompt: str

    class Config:
        from_attributes = True

