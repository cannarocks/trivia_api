import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
from flask_cors import CORS
import random
from sqlalchemy.exc import SQLAlchemyError
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(req, items):
    page = req.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in items]

    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/')
    def home():
        return jsonify({
            'success': True,
            'message': "Welcome to Trivia API",
            'routes': ['questions', 'categories', 'quizzes']
        })

    '''
         Get Question: 
         Create an endpoint to handle GET requests for questions, 
         including pagination (every 10 questions). 
         This endpoint should return a list of questions, 
         number of total questions, current category, categories. 

         TEST: At this point, when you start the application
         you should see questions and categories generated,
         ten questions per page and pagination at the bottom of the screen for three pages.
         Clicking on the page numbers should update the questions. 
    '''

    @app.route('/questions', methods=['GET'])
    def get_questions():
        items = Question.query.order_by(Question.id).all()
        selection = paginate_questions(request, items)

        if len(selection) == 0:
            abort(404)

        categories = Category.query.order_by(Category.id).all()

        return jsonify({
            'success': True,
            'questions': selection,
            'current_category': None,
            'categories': [category.format() for category in categories],
            'total_questions': len(Question.query.all())
        })

    '''
    Get single Question
    '''

    @app.route('/questions/<int:question_id>', methods=['GET'])
    def get_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        return jsonify({
            'success': True,
            'question': question.format()
        })

    ''' 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        items = Category.query.order_by(Category.id).all()

        if len(items) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': [category.format() for category in items]
        })

    ''' 
    Endpoint to handle GET requests 
    for single categories.
    '''
    @app.route('/categories/<int:category_id>', methods=['GET'])
    def get_single_category(category_id):
        category = Category.query.get(category_id)

        if category is None:
            abort(404)

        return jsonify({
            'success': True,
            'category': category.format()
        })

    @app.route('/questions/<int:question_id>', methods=['PATCH'])
    def update_question(question_id):
        question = Question.query.get(question_id)
        success = True

        if question is None:
            abort(404)

        body = request.get_json()

        if body.get('question') is not None:
            question.question = body.get('question')

        if body.get('answer') is not None:
            question.answer = body.get('answer')

        try:
            question.update()
        except SQLAlchemyError as e:
            success = False

        return jsonify({
            'success': success,
            'question': question.format()
        })

    '''
  Delete Question 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        question.delete()

        return jsonify({
            'success': True,
            'total_questions': len(Question.query.all())
        })

    '''
  Add new question 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    @app.route('/questions', methods=['POST'])
    def add_new_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        try:
            question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            question.insert()
        except SQLAlchemyError:
            abort(500)

        return jsonify({
            'success': True,
            'question': question.id,
            'total_question': len(Question.query.all())
        })

    '''
  Search Questions 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    @app.route('/questions/search', methods=['POST'])
    def find_question():
        body = request.get_json()

        if body is None or body.get('searchTerm', None) is None:
            '''Return unfiltered questions'''
            results = Question.query.order_by(Question.id).all()
        else:
            term = body.get('searchTerm').lower()
            print(term)
            results = Question.query.filter(
                or_(
                    func.lower(Question.question).like(f'%{term}%'),
                )
            ).all()

        return jsonify({
            'success': True,
            'questions': [question.format() for question in results],
            'current_category': None,
            'total_questions': len(results)
        })

    '''
  Get Question By Category 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        items = Question.query.filter_by(category=category_id).all()
        selection = paginate_questions(request, items)

        if len(selection) == 0:
            abort(404)

        category = Category.query.get(category_id)

        return jsonify({
            'success': True,
            'questions': selection,
            'current_category': category.type,
            'total_questions': len(Question.query.all())
        })

    '''
  Play Quiz 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()

        if body is None:
            abort(422)

        previous_questions = body.get('previous_questions', [])
        category = body.get('quiz_category', None)

        if category is None or category.get('id') == 0:
            question = Question.query.filter(~Question.id.in_(previous_questions)).order_by(func.random()).first()
        else:
            question = Question.query.filter(
                Question.category == category.get('id'),
                ~Question.id.in_(previous_questions)).order_by(func.random()).first()

        return jsonify({
            'success': True,
            'question': False if question is None else question.format()
        })

    ''' 
  Error handlers for all expected errors 
  including 404 and 422. 
  '''

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify(success=False, error=404, message="Route not found"), 404

    @app.errorhandler(422)
    def unprocessable_error(error):
        return jsonify(success=False, error=422, message="Unprocessable request"), 422

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify(success=False, error=500, message="Internal server error"), 500

    @app.errorhandler(405)
    def not_allowed_error(error):
        return jsonify(success=False, error=405, message="Method not allowed"), 405

    return app
