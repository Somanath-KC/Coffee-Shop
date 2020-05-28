import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

cors = CORS(app, resources={r"*": {"origin": "*"}})
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response


'''
@TODO:[COMPLETED] uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO:[COMPLETED] implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
@TODO[COMPLTED] implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = [drink.long() for drink in Drink.query.all()]

    return jsonify({
        'status': True,
        'drinks': drinks
    })


'''
@TODO:[COMPLETED] implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:
        data = request.get_json()
        try:
            new_drink = Drink()
            new_drink.title = data.get('title')
            new_drink.recipe = json.dumps(data.get('recipe'))
        except:
            return jsonify({
                'status': False,
                'error': 400,
                'message': 'Invalid body'
            }), 400
        new_drink.insert()
    except Exception as e:
        # Print statements for debugging
        print(e)
        abort(422)

    return jsonify({
        'success': True,
        'drinks': new_drink.long()
    })


'''
@TODO:[COMPLETED] implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):

    drink = Drink.query.get(drink_id)

    if not drink:
        abort(404)

    data = request.get_json()

    title = data.get('title')
    recipe = data.get('recipe')

    # Checks which part of the drink to be updated
    if title:
        drink.title = title
    if recipe:
        drink.recipe = recipe
    
    try:
        drink.update()
        return jsonify({
            'status': True,
            'drinks': drink.long()
        })
    except Exception as e:
        # Print statements for debugging
        print(e)
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO:[COMPLETED] implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def notFoundError(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "respurce not found"
            }), 404

@app.errorhandler(500)
def internal_errors(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': "API Internal Error"
    }), 500

'''

@TODO:[COMPLETED] implement error handler for AuthError
    error handler should conform to general task above 
'''
# Refrence: 
#          https://flask.palletsprojects.com/en/1.1.x/patterns/apierrors/#registering-an-error-handler
@app.errorhandler(AuthError)
def auth_errors(auth_error):
    error = auth_error.error
    return jsonify({
        'success': False,
        'error': error.get('error'),
        'message': error.get('message')
    }), auth_error.status_code
