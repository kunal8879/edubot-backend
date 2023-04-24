import requests
from model import ChatBotModel as chatbot_model
from datetime import datetime

# backend url for testing
url = 'http://127.0.0.1:8000/edubot'

# test question
question = chatbot_model.ChatBotModel(user="bot", sentence='hello', time=datetime.now().strftime("%H:%M:%S"))

# send question to backend api
answer = requests.post(url, json=question).json()

# print the answer
print(answer)
