from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
# import pickle
# import json

import edubot_model

appAPI = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:4200",
]

appAPI.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class frontendmodel(BaseModel):
    sentence: str


class model(BaseModel):
    author: str
    sentence: str
    time: str


# get request for edubot to get answer from ml model
@appAPI.post("/edubot")
def edubot_post(message: model):

    # question = input_data.json()
    # print(input_data)

    question = message.sentence
    # print(question)

    answer = edubot_model.response(question)
    # print(answer)
    return model(author='bot', sentence=answer, time=datetime.now().strftime("%H:%M:%S"))
