from fastapi import FastAPI
from py.model import ChatBotModel as chatbot_model
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from py.ml_model import edubot_model

# create FastAPI app
appAPI = FastAPI()

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
def edubot_post(chat_question: chatbot_model.ChatBotModel):
    # getting the response from the edubot_model
    answer = edubot_model.response(chat_question.sentence)
    # returning the response to the frontend
    return chatbot_model.ChatBotModel(author='bot', sentence=answer, time=datetime.now().strftime("%H:%M:%S"))
