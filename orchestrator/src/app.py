import sys
import os
from concurrent.futures import ThreadPoolExecutor
from jsonschema import validate
import json

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path1 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
utils_path2 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
utils_path3 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_ver'))

sys.path.insert(0, utils_path1)
sys.path.insert(0, utils_path2)
sys.path.insert(0, utils_path3)

import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc
import transaction_ver_pb2 as transaction_ver
import transaction_ver_pb2_grpc as transaction_ver_grpc

import grpc




def verify_transaction(transaction_data):
    with grpc.insecure_channel('transaction_ver:50052') as channel:
        stub = transaction_ver_grpc.TransactionVerificationServiceStub(channel)

        # Make data suitable for proto file
        transaction_data = transaction_ver.Transaction(
            user=transaction_ver.User(
                name=transaction_data['user']['name'],
                contact=transaction_data['user']['contact']
            ),
            credit_card=transaction_ver.CreditCard(
                number=transaction_data['creditCard']['number'],
                expirationDate=transaction_data['creditCard']['expirationDate'],
                cvv=transaction_data['creditCard']['cvv']
            )
        )

        # verification request
        response = stub.VerifyTransaction(
            transaction_ver.VerifyTransactionRequest(transaction=transaction_data))
        return response


def getBookSuggestions(data):
    id = data['items'][0]['id']
    with grpc.insecure_channel('suggestions:50053') as channel:
        # Create a stub object.
        stub = suggestions_grpc.SuggestionsServiceStub(channel)
        # Call the service through the stub object.
        response = stub.getSuggestions(suggestions.getSuggestionsRequest(bookid = id))
    return response.items

def detectFraud(data):
    total_qty = data['items'][0]['quantity']
    # Connect to the fraud detection service.
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        # Call the service through the stub object.
        response = stub.FraudDetection(fraud_detection.FraudRequest(total_qty=total_qty))
    return response



# Import Flask.
# Flask is a web framework for Python.
# It allows you to build a web application quickly.
# For more information, see https://flask.palletsprojects.com/en/latest/
from flask import Flask, request, jsonify
from flask_cors import CORS

# Create a simple Flask app.
app = Flask(__name__)
# Enable CORS for the app.
CORS(app)

# Define a GET endpoint.
@app.route('/', methods=['GET'])
def index():
    """
    Responds with 'Hello, [name]' when a GET request is made to '/' endpoint.
    """
    # Test the fraud-detection gRPC service.
    response = 'Hello, World!'
    # Return the response.
    return response

@app.route('/checkout', methods=['POST'])
def checkout():
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """
    data = request.json
    # Print request object data
    print("Request Data:", request.json)

    with open('orchestrator/src/schema.json') as f:
        schema = json.load(f)

    try:
        validate(instance=data, schema=schema)
    except Exception as e:
        print(f"Schema validation failed: {e}")
        return {"error": {"code": "400", "message": f"Schema validation failed: {e}"}}, 400

    functions = [verify_transaction, detectFraud, getBookSuggestions]

    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit tasks to the thread pool
            futures = [executor.submit(f, data) for f in functions]

            # Wait for all tasks to complete
            verification_response, fraud_response, book_suggestions = [future.result() for future in futures]
    except Exception as e:
        print(e)


    print(f"verification respnse: {verification_response}")
    print(f"fraud response: {fraud_response}")
    print(f"book suggestions: {book_suggestions}")



    if verification_response.is_valid and fraud_response.is_valid:
        order_status_response = {
            'orderId': '12345',
            'status': 'Order Approved',
            'suggestedBooks': [
                {'bookId': book.bookid, 'title': book.title, 'author': book.author} for book in book_suggestions
            ]
        }

    else:
        order_status_response = {
            'orderId': '12345',
            'status': "Order Rejected",
        }
        # Dummy response following the provided YAML specification for the bookstore
        # order_status_response = {
        #     'orderId': '12345',
        #     'status': "",
        #     'suggestedBooks': [
        #         {'bookId': '123', 'title': 'Dummy Book 1', 'author': 'Author 1'},
        #         {'bookId': '456', 'title': 'Dummy Book 2', 'author': 'Author 2'}
        #     ]
        # }

    print(order_status_response)
    return jsonify(order_status_response)


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
