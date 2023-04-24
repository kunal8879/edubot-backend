from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from py.db_config import SessionLocal, engine
from py.model import models as models
from py.ml_model import edubot_ml

import py.model.entities as entities

# create FastAPI app
appAPI = FastAPI()

# creating tables
entities.Base.metadata.create_all(bind=engine)


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
def edubot_post(chat_question: models.ChatBotModel, db: Session = Depends(get_db)):
    try:
        # getting the response from the edubot_model
        answer = edubot_ml.response(chat_question.chat)

        # saving the question to the database if no answer is found
        if answer == "Sorry I have no answer for that question right now. Please share you mail id for further assistance.":
            new_question = entities.Question()
            new_question.chat = chat_question.chat
            new_question.time = datetime.now()
            db.add(new_question)
            db.commit()

        return models.ChatBotModel(
            author='bot',
            chat=answer,
            time=datetime.now().strftime("%H:%M:%S")
        )
    except Exception as e:
        print(e)
        return models.ChatBotModel(
            author='bot',
            chat="Sorry I have no answer for that question right now. Please share you mail id for further assistance.",
            time=datetime.now().strftime("%H:%M:%S")
        )


# admin registration
@appAPI.post("/admin/register")
def admin_register(admin: models.Admin, db: Session = Depends(get_db)):
    try:
        # checking if the username already exists
        if db.query(entities.Admin).filter(entities.Admin.username == admin.username).first():
            return models.Admin(
                id='0',
                username='0',
                password='0'
            )
        else:
            # saving the new admin to the database
            new_admin = entities.Admin()
            new_admin.username = admin.username
            new_admin.password = admin.password
            db.add(new_admin)
            db.commit()

            return models.Admin(
                id=new_admin.id,
                username=new_admin.username,
                password=new_admin.password
            )
    except Exception as e:
        print(e)
        return models.Admin(
            id='0',
            username='0',
            password='0'
        )


@appAPI.get("/unanswered_questions")
def unanswered_questions(db: Session = Depends(get_db)):
    try:
        # getting all the unanswered questions from the database
        questions = db.query(entities.Question).all()

        # converting the questions to a list of dictionaries
        questions_list = []
        for question in questions:
            questions_list.append({
                "id": question.id,
                "chat": question.chat,
                "time": question.time
            })

        return questions_list
    except Exception as e:
        print(e)
        return []


@appAPI.post("/login")
def login(admin: models.Login, db: Session = Depends(get_db)):
    try:
        # checking if the username and password are correct
        if db.query(entities.Admin).filter(entities.Admin.username == admin.username).filter(entities.Admin.password == admin.password).first():
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


@appAPI.post("/newUser")
def new_user(user: models.User, db: Session = Depends(get_db)):
    try:
        # saving the new user to the database
        user_new = entities.Users()
        user_new.email = user.email
        user_new.new_question = user.new_question
        user_new.time = user.time
        db.add(user_new)
        db.commit()

        return models.ChatBotModel(
            author='bot',
            chat='Thank you for your question. We will get back to you soon.',
            time=datetime.now().strftime("%H:%M:%S")
        )

    except Exception as e:
        print(e)
        return models.User(
            id='0',
            email='0',
            time='0'
        )


@appAPI.get("/users")
def users(db: Session = Depends(get_db)):
    try:
        # getting all the users from the database
        user_list = db.query(entities.Users).all()

        # converting the users to a list of dictionaries
        users_list = []
        for user in user_list:
            users_list.append({
                "id": user.id,
                "email": user.email,
                "new_question": user.new_question,
                "time": user.time
            })

        return users_list
    except Exception as e:
        print(e)
        return []
