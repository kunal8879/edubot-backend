# Importing Libraries required for NLP
import nltk

from nltk.stem.lancaster import LancasterStemmer

from fastapi import FastAPI
from pydantic import BaseModel

appAPI = FastAPI()

stemmer = LancasterStemmer()

# Importing Libraries needed for Tensorflow processing
import tensorflow as tf  # version 1.13.2
import numpy as np
import tflearn  # version 0.3.2
import random
import json
import pickle

intents = json.loads(open("intents.json").read())

# importing our intent file used for training the model.
# with open("intents.json") as json_data:
#     intents = json.load(json_data)      # Loading data from intents.json file to var intents

# Empty lists for appending the data after processing NLP
words = []
documents = []
classes = []

# This list will be used for ignoring all unwanted punctuation marks.
ignore = ["?", ".", "!", ","]

# Starting a loop through each intent in intents["patterns"]
for intent in intents["intents"]:
    for pattern in intent["patterns"]:

        # tokenizing each and every word in the sentence by using word tokenizer and storing in w
        w = nltk.word_tokenize(pattern)
        # print(w)

        # Adding tokenized words to words empty list that we created
        words.extend(w)
        # print(words)

        # Adding words to documents with tag given in intents file
        documents.append((w, intent["tag"]))
        # print(documents)

        # Adding only tag to our classes list
        if intent["tag"] not in classes:
            classes.append(intent["tag"])  # If tag is not present in classes[] then it will append into it.
            # print(classes)

# Performing Stemming by using stemmer.stem() nd lower each word
# Running loop in words[] and ignoring punctuation marks present in ignore[]

words = [stemmer.stem(w.lower()) for w in words if w not in ignore]
words = sorted(list(set(words)))  # Removing Duplicates in words[]

# Removing Duplicate Classes
classes = sorted(list(set(classes)))

# Printing length of lists we formed
print(len(documents), "Documents \n")
print(len(classes), "Classes \n")
print(len(words), "Stemmed Words ")

# Creating Training Data which will be further used for training
training = []
output = []

# Creating empty array for output
output_empty = [0] * len(classes)

# Creating Training set and bag of words for each sentence
for doc in documents:
    bag = []  # Initialising empty bag of words

    pattern_words = doc[0]  # Storing list of tokenized words for the documents[] tp pattern_words
    # print(pattern_words)

    # Again Stemming each word from pattern_words
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
    # print(pattern_words)

    # Creating bag of words array
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

        # It will give output 1 for current tag and 0 for all other tags
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)  # Shuffling the data or features
training = np.array(training)  # Converting training data into numpy array

# Creating Training Lists
train_x = list(training[:, 0])
train_y = list(training[:, 1])

tf.compat.v1.reset_default_graph()  # Reset Underlying Graph data

# Building our own Neural Network
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 10)
net = tflearn.fully_connected(net, 10)
net = tflearn.fully_connected(net, len(train_y[0]), activation="softmax")
net = tflearn.regression(net)

# Defining Model and setting up tensorboard
model = tflearn.DNN(net, tensorboard_dir="tflearn_logs")

# Now we have setup model, now we need to train that model by fitting data into it by model.fit()
# n_epoch is the number of times that model will se our data during training
model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
model.save("model.sav")  # Saving the model

# Importing pickle module
import pickle

# Dumping training data by using dump() and writing it into training_data in binary mode
pickle.dump({"words": words, "classes": classes, "documents": documents, "train_x": train_x, "train_y": train_y},
            open("training_data", "wb"))

# Restoring all data structure
data = pickle.load(open("training_data", "rb"))
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']
with open("training_data", "rb") as f:
    mp = pickle.load(f)
    # print(mp)

# Loading the saved model
model.load("./model.sav")  # Loading training model which we saved


# Cleaning User Input
def clean_up_sentence(sentence):
    # Tokenizing the pattern
    sentence_words = nltk.word_tokenize(sentence)  # Again tokenizing the sentence

    # Stemming each word from the user's input
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]

    return sentence_words


# Returning bag of words array: 0 or 1 or each word in the bag that exists in as we have declared in above lines
def bow(sentence, words, show_details=False):
    # Tokenizing the user input
    sentence_words = clean_up_sentence(sentence)

    # Generating bag of words from the sentence that user entered
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("Found in bag: %s" % w)
    return np.array(bag)


# Adding some context to the conversation for better results.

context = {}  # Create a dictionary to hold user's context

ERROR_THRESHOLD = 0.5


def classify(sentence):
    # Generating probabilities from the model
    results = model.predict([bow(sentence, words)])[0]

    # Filter out predictions below a threshold
    results = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]

    # Sorting by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))

    # return tuple of intent and probability
    return return_list


def response(sentence, userID='123', show_details=False):
    results = classify(sentence)

    # If we have a classification then find the matching in
    # tent tag
    if results:

        # Loop as long as there are matches to process
        while results:
            for i in intents['intents']:

                # Find a tag matching the first result
                if i['tag'] == results[0][0]:

                    # Set context for this intent if necessary
                    if 'context_set' in i:
                        if show_details: print('context:', i['context_set'])
                        context[userID] = i['context_set']

                    # check if this intent is contextual and applies to this user's conversation
                    if not 'context_filter' in i or \
                            (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print('tag:', i['tag'])

                        # A random response from the intent
                        return random.choice(i['responses'])

            results.pop(0)
    else:
        return "no such answer found"


# def getinput(question: str):
#     return model.predict(question)


# while True:
#     input = input("question: ")


# response("what is your name?")
# response("what is your age?")
# response("hod of computer engineering?")
# response("hii")
# response("address of college?")
# response("phone number of college?")
# response("goodbye")
