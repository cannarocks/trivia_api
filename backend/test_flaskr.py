import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, get_db_path, Question, Category
from dotenv import load_dotenv

load_dotenv('.env')


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        self.database_name = os.environ.get("TEST_DB_NAME", default="trivia_test")
        db_user = os.environ.get("DB_USER", default="guest")
        db_psw = os.environ.get("DB_PSW", default="guest")
        db_port = os.environ.get("DB_PORT", default=54333)

        self.database_path = f"postgresql://{db_user}:{db_psw}@localhost:{db_port}/{self.database_name}"

        setup_db(self.app, self.database_path)

        """ binds the app to the current context """
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    For a success response we expect a 200 status code with a success equals to True
    """

    def is_response_ok(self, res, data):
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def execute_request(self, endpoint, method="get", body=None):
        res = getattr(self.client(), method)(endpoint, body)
        data = json.loads(res.data)

        return [res, data]

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_root(self):
        res, data = self.execute_request('/')
        self.is_response_ok(res, data)

    def test_get_questions(self):
        res, data = self.execute_request('/questions')
        self.is_response_ok(res, data)

        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
