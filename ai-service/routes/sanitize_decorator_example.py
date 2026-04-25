"""
This file shows how to use @sanitise_request_body decorator on a Flask route

** This is not a real route file. It is an example to show how to plug in the sanitisation decorator 

"""

from flask import Blueprint, request, jsonify
from middleware.input_sanitize import sanitize_request_body

example_bp = Blueprint('example',__name__)

@example_bp.route('/describe', methods=['POST'])
@sanitize_request_body(['text','context'])        # list the fields to sanitize
def describe():
    """
    decorator runs before this function
    any security checks failed, http 400 response is returned before the function is executed
    """
    data = request.get_json()
    text = data['text']
    context = data.get('context', '')
    return jsonify({
        "message": "describe endpoint"
    }),200
