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

        self.new_question = {
            "question": "Who won the 2006 Fifa World Cup?",
            "answer": "France",
            "category": "6",
            "difficulty": "1"
        }

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
        res = getattr(self.client(), method)(endpoint, json=body)
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

    def test_get_single_question(self):
        res, data = self.execute_request('/questions/2')
        self.is_response_ok(res, data)
        self.assertTrue(data['question'])

    def test_add_question(self):
        res, data = self.execute_request('/questions', 'post', self.new_question)
        self.is_response_ok(res, data)
        self.assertGreater(data['question'], 0)

    def test_update_question(self):
        res, data = self.execute_request('/questions/24', 'patch', {'answer': 'Italy'})
        self.is_response_ok(res, data)

    def test_delete_question(self):
        res, data = self.execute_request('/questions', 'post', self.new_question)
        if data['success']:
            question_id = data['question']
            res, data = self.execute_request(f'/questions/{question_id}', 'delete')
            self.is_response_ok(res, data)

    def test_get_categories(self):
        res, data = self.execute_request('/categories')
        self.is_response_ok(res, data)

        self.assertTrue(len(data['categories']))

    def test_get_single_category(self):
        res, data = self.execute_request('/categories/1')
        self.is_response_ok(res, data)

        self.assertTrue(data['category'])

    def test_not_found_questions(self):
        res, data = self.execute_request('/questions/999')
        self.assertEqual(res.status_code, 404)

    def test_not_found_categories(self):
        res, data = self.execute_request('/categories/999')
        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
