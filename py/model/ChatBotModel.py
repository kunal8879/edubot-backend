from pydantic import BaseModel


# ChatBotModel
class ChatBotModel(BaseModel):
    author: str
    chat: str
    time: str
