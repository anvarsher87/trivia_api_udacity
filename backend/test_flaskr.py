import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        
        self.database_path = "postgresql://{}:{}@{}/{}".format("postgres", "1", "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    # Categories
     
    def test_get_categories(self):
        res  = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["total_categories"])
    
    def test_retrieve_categories_404(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        if len(data["categories"]) == 0:
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data["success"], False)    
    
    # Questions

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))

    def test_retrieve_questions_404(self):
        res = self.client().get("/questions?page=10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
    
    # Delete 

    def test_delete_question(self):
        # Creating a sample question
        question = Question(question ="Test question for deleting APi",
                            answer = 'Answer to the test',
                            difficulty=2,
                            category=1)
        question.insert()
        question_id = question.id

        # Sending a delete request to the endpoint
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        # Checking the api response
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        question = Question.query.filter(Question.id == question_id).one_or_none()
        self.assertEqual(question, None)
    
    def test_delete_question_404(self):
        res = self.client().delete("/questions/123456789")
        data = json.loads(res.data)

        if data is None:
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data["success"], False)

    def test_422_if_question_not_exist(self):
        res = self.client().delete('/questions/123456789')
        data = json.loads(res.data)
        # Check the response
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False) 
    
    # TDD for creating questions
    def test_create_question(self):
        new_question = {
                       'question': 'Test question for creating a new question',
                       'answer': 'Answer to the test',
                       'difficulty': 2,
                       'category': 1
                       }
        res = self.client().post("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        question = Question.query.filter(Question.question == new_question['question']).one_or_none()
        self.assertIsNotNone(question)
    
    def test_create_question_422(self):
        new_question = {
        'question': '',
        'answer': '',
        'difficulty': 2,
        'category': 'one'  # this intentionally made string instead of integer
         }
        res = self.client().post("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
    
    # Searching questions

    def test_search_questions(self):
        res = self.client().post('/search', json={'searchTerm': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)
    
    def test_search_questions_422_error(self):
        
        res = self.client().post('/search', json={})
        self.assertEqual(res.status_code, 422)


    def test_get_quiz_questions(self):
        res = self.client().post('/quizzes', json={
        'quiz_category': {'type': 'Science', 'id': 1},
        'previous_questions': [1, 2, 3]
         })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])

    def test_get_quiz_questions_404_error(self):
        
        res = self.client().post('/quizzes', json={'previous_questions': [5, 9, 12], 'quiz_category': {'id': 4}})
        data = json.loads(res.data)
        

        self.assertEqual(data['error'], 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'No more question available')







    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()