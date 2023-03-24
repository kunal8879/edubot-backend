import json
import requests
import main


url = 'http://127.0.0.1:8000/edubot'

question = main.frontendmodel(sentence='hello')

print(question.sentence)

myobj = {'sentence': 'hello'}
# # input_json = json.dumps(mlModel)
#
#

answer = requests.post(url, json=myobj)

print(answer.content)
