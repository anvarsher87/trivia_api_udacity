import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app,supports_credentials=True)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers','GET, POST, PATCH, DELETE, OPTIONS')
        return response
    

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()
        categories = {category.id: category.type for category in selection}
        if len(categories) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(Category.query.all()),
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=["GET"])
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        categories_selection = Category.query.order_by(Category.id).all()
        categories = {category.id: category.type for category in categories_selection}

        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories':categories,
            'total_questions': len(Question.query.all()),
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
               abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions=paginate_questions(request, selection)


            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                })

        except:
           abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=["POST"])
    def create_question():
        body = request.get_json()
        try:
            new_question = Question(question=body.get("question"), 
                                    answer=body.get("answer"),
                                    difficulty=body.get("difficulty"), 
                                    category=body.get("category"))
            new_question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions=paginate_questions(request, selection)
            
         

            return jsonify(
              {
               "success": True,
               "created": new_question.id,
               'questions': current_questions,
               'total_questions': len(Question.query.all()),
               }
              )

        except:
          
            abort(422)


    @app.route('/search', methods=["POST"])
    def search_questions():
        body = request.get_json()
        search = body.get("searchTerm", None)
       
        try:
            
            if search:
                
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search)))
                current_questions = paginate_questions(request, selection)
                
                return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(selection.all()),
                }
            )
            else:
                
                abort(400)

        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions(category_id):
        selection = Question.query.filter_by(category=category_id).all()
        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions_in_category': len(Question.query.filter_by(category=category_id).all()),
        })


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

     
    from random import choice
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        data = request.get_json()
        category = data.get('quiz_category')
        previous_questions = data.get('previous_questions')

        if int(category['id']) > 0:
            questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_(previous_questions)).all()
          
        else:
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()

        if not questions:
            
            return jsonify({
            'success': False,
            'error': 404,
            'message': 'No more question available'
            })

        else:
            question = choice(questions).format()
            
        return jsonify({
        'success': True,
        'question': question
        })


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    return app

