import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json


# From .env var returns the db path
def get_db_path(test_env=False):
    db_name = os.environ.get("TEST_DB_NAME", default="trivia_test") if test_env else os.environ.get("DB_NAME", default="trivia")
    db_user = os.environ.get("DB_USER", default="guest")
    db_psw = os.environ.get("DB_PSW", default="guest")
    database_port = int(os.environ.get("DB_PORT", default=54333))
    return f"postgresql://{db_user}:{db_psw}@localhost:{database_port}/{db_name}"


database_path = get_db_path()
db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_uri=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = bool(os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS"))
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Question

'''


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


'''
Category

'''


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
