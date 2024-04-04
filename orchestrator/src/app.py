import sys
import os
from concurrent.futures import ThreadPoolExecutor
from jsonschema import validate
import json
from multiprocessing import Value

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path1 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
utils_path2 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
utils_path3 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_ver'))
utils_path4 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))

sys.path.insert(0, utils_path1)
sys.path.insert(0, utils_path2)
sys.path.insert(0, utils_path3)
sys.path.insert(0, utils_path4)

import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc
import transaction_ver_pb2 as transaction_ver
import transaction_ver_pb2_grpc as transaction_ver_grpc
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

import grpc

from utils.pb.transaction_ver.transaction_ver_pb2 import VectorClock
from utils.pb.suggestions.suggestions_pb2 import VectorClock

order_id_count = Value('i', 0)


def enqueue_order(order_id, order_data):
    print(f">> Enqueueing order: {order_id}")
    try:
        with grpc.insecure_channel('order_queue:50054') as channel:
            stub = order_queue_grpc.OrderQueueServiceStub(channel)
            order_message = order_queue.Order(orderId=str(order_id),
                                              userName=order_data['user']['name'])
        response = stub.EnqueueOrder(order_queue.EnqueueRequest(order=order_message))
        print(f">> Order enqueued: {response}")
    except Exception as e:
        print(f"Exception in enqueue_order: {e}")
        return {"error": {"code": "500", "message": "Internal Server Error"}}, 500

    return response


def verify_transaction(transaction_data, vector_clock):
    with grpc.insecure_channel('transaction_ver:50052') as channel:
        stub = transaction_ver_grpc.TransactionVerificationServiceStub(channel)

        if type(transaction_data["items"]) == dict:
            transaction_data["items"] = [transaction_data["items"]]

        print(f">> Transaction data: {transaction_data}")

        # Make data suitable for proto file
        transaction_data = transaction_ver.Transaction(
            items=[transaction_ver.Item(
                bookid=item['id'],
                quantity=item['quantity']
            ) for item in transaction_data['items']],
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
        print(f">> Before response")
        try:
            response = stub.VerifyTransaction(transaction_ver.VerifyTransactionRequest(
                transaction=transaction_data,
                vector_clock=transaction_ver.VectorClock(clock=vector_clock.clock)))
        except Exception as e:
            print(f"Exception in verify_transaction: {e}")
            return {"error": {"code": "500", "message": "Internal Server Error"}}, 500
        print(f">> After response")
        return response


def getBookSuggestions(data, vector_clock):
    id = data['items'][0]['id']
    with grpc.insecure_channel('suggestions:50053') as channel:
        # Create a stub object.
        stub = suggestions_grpc.SuggestionsServiceStub(channel)
        # Call the service through the stub object.
        response = stub.getSuggestions(suggestions.getSuggestionsRequest(bookid=id))
        try:
            print(f"before response")
            request = suggestions.getSuggestionsRequest(bookid=id,
                vector_clock=suggestions.VectorClock(clock=vector_clock.clock))
            response = stub.getSuggestions(request)
            print(f"after response")
        except Exception as e:
            print(f"Exception in getBookSuggestions: {e}")
            return {"error": {"code": "500", "message": "Internal Server Error"}}, 500
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
    with order_id_count.get_lock():
        vector_clock = VectorClock(clock={'order_id': order_id_count.value,
                                          'transaction_ver': 0,
                                          'fraud_detection': 0,
                                          'suggestions': 0, })
        order_id_count.value += 1
    data = request.json
    # Print request object data
    print(f">> Request Data: {request.json}")

    with open('orchestrator/src/schema.json') as f:
        schema = json.load(f)

    try:
        validate(instance=data, schema=schema)
    except Exception as e:
        print(f"Schema validation failed: {e}")
        return {"error": {"code": "400", "message": f"Schema validation failed: {e}"}}, 400

    try:
        functions = [verify_transaction, getBookSuggestions]
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit tasks to the thread pool
            futures = [executor.submit(f, data, vector_clock) for f in functions]

            # Wait for all tasks to complete
            verification_response, book_suggestions_response = [future.result() for future in futures]

        for key in verification_response.vector_clock.clock.keys():
            vector_clock.clock[key] = max(verification_response.vector_clock.clock[key],
                                          book_suggestions_response.vector_clock.clock[key])

        print(f">> Vector clock: {vector_clock}")
        verification_response = verify_transaction(data, vector_clock)
        print(f">> Verification and Fraud Response: {verification_response}")

        if verification_response.is_valid:
            queue_response = enqueue_order(vector_clock.clock['order_id'], data)
            if queue_response.success:
                order_status_response = {
                    'orderId': vector_clock.clock['order_id'],
                    'status': "Order Approved",
                    'suggestedBooks': [
                        {'bookId': book.bookid, 'title': book.title, 'author': book.author}
                        for book in book_suggestions_response.items
                    ]
                }
            else:
                order_status_response = {
                    'orderId': vector_clock.clock['order_id'],
                    'status': "We were unable to process your order. Please try again later."
                }

        else:
            order_status_response = {
                'orderId': vector_clock.clock['order_id'],
                'status': "Order Rejected",
            }

    except Exception as e:
        print(f">> Error during paralles processing of microservices {e}")
        return {"error": {"code": "500", "message": "Internal Server Error"}}, 500

    print(order_status_response)
    return order_status_response, 200


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
