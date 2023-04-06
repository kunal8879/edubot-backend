from pydantic import BaseModel


# ChatBotModel
class Admin(BaseModel):
    id: str
    username: str
    password: str
