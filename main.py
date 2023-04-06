from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from py.db_config import SessionLocal, engine
from py.model import ChatBotModel as chatbot_model
from py.ml_model import edubot_model

import py.model.models as models

# create FastAPI app
appAPI = FastAPI()

# creating tables
models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# allowing the frontend url to access the appAPI
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:4200",
]

# adding middleware to the appAPI
appAPI.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# post request to get answer from edubot_model
@appAPI.post("/edubot")
def edubot_post(chat_question: chatbot_model.ChatBotModel, db: Session = Depends(get_db)):
    try:
        # getting the response from the edubot_model
        answer = edubot_model.response(chat_question.chat)

        # saving the question to the database if no answer is found
        if answer == "Sorry I have no answer for that question":
            new_question = models.Question()
            new_question.chat = chat_question.chat
            new_question.time = datetime.now()
            db.add(new_question)
            db.commit()

        return chatbot_model.ChatBotModel(
            author='bot',
            chat=edubot_model.response(chat_question.chat),
            time=datetime.now().strftime("%H:%M:%S")
        )
    except Exception as e:
        print(e)
        return chatbot_model.ChatBotModel(
            author='bot',
            chat="Something went wrong, please try again later",
            time=datetime.now().strftime("%H:%M:%S")
        )
