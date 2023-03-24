from pydantic import BaseModel


# ChatBotModel
class ChatBotModel(BaseModel):
    author: str
    sentence: str
    time: str
