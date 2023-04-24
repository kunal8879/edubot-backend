from pydantic import BaseModel


class ChatBotModel(BaseModel):
    author: str
    chat: str
    time: str


class Admin(BaseModel):
    id: str
    username: str
    password: str


class Login(BaseModel):
    username: str
    password: str


class User(BaseModel):
    email: str
    new_question: str
    time: str
