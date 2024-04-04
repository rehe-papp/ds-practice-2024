import sys
import os
import datetime

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_ver'))
utils_path2 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))

sys.path.insert(0, utils_path)
sys.path.insert(0, utils_path2)

import transaction_ver_pb2 as transaction_ver
import transaction_ver_pb2_grpc as transaction_ver_grpc
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc


import grpc
from concurrent import futures
import re

#needs full path
from utils.pb.fraud_detection.fraud_detection_pb2 import VectorClock

def detectFraud(data, vector_clock):
    """
    fraud detection service
    """
    vector_clock.clock['fraud_detection'] += 1
    print(f">> fraud detection vector_clock updated: {vector_clock}")

    total_qty = data.items[0].quantity

    # Connect to the fraud detection service.
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        # Call the service through the stub object.
        try:
            response = stub.FraudDetection(fraud_detection.FraudRequest(total_qty=total_qty,
                                                                        vector_clock=fraud_detection.VectorClock(clock=vector_clock.clock)))
            print(f">> response {response}")
            return response
        except Exception as e:
            return transaction_ver.VerifyTransactionResponse(is_valid=False,
                                                             error_message=f"Exception in detectFraud: {e}",
                                                             vector_clock=vector_clock)

class TransactionVerificationService(transaction_ver_grpc.TransactionVerificationServiceServicer):
    def VerifyTransaction(self, request, context):
        print(f">> Transaction verification service called. {request.vector_clock}")
        request.vector_clock.clock['transaction_ver'] += 1
        print(f">> Transaction verification vector clock updated: {request.vector_clock}")

        if not request.transaction.user or not request.transaction.user.name or not request.transaction.user.contact:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Missing user name or contact')
            return transaction_ver.VerifyTransactionResponse(is_valid=False,
                                                             error_message='Missing user name or contact',
                                                             vector_clock=request.vector_clock)
        print(">> Transaction verification service user name and contact verified.")
        request.vector_clock.clock['transaction_ver'] += 1
        if not re.match(r'^[0-9]{16}$', request.transaction.credit_card.number):
            return transaction_ver.VerifyTransactionResponse(is_valid=False,
                                                             error_message="Invalid credit card number.",
                                                             vector_clock=request.vector_clock)
        print(">> Transaction verification service credit card number verified.")
        request.vector_clock.clock['transaction_ver'] += 1

        current_year, current_month = datetime.datetime.today().year, datetime.datetime.today().month
        expiration_date = request.transaction.credit_card.expirationDate
        expiration_month, expiration_year = map(int, expiration_date.split('/'))
        expiration_year += 2000  # Year to correct format
        # Check if credit card expiration month correctness
        if expiration_month > 12:
            return transaction_ver.VerifyTransactionResponse(is_valid=False,
                                                             error_message="Invalid credit card expiration date.",
                                                             vector_clock=request.vector_clock)
        print(">> Transaction verification service credit card expiration month verified.")
        #Check to see if credit card has expired
        if (expiration_year, expiration_month) < (current_year, current_month):
            return transaction_ver.VerifyTransactionResponse(is_valid=False,
                                                             error_message="Credit card is expired or .",
                                                             vector_clock=request.vector_clock)
        print(">> Transaction verification service credit card expiration date verified.")
        request.vector_clock.clock['transaction_ver'] += 1
        try:
            print(">> Transaction verification service called fraud detection service.")
            return detectFraud(request.transaction, request.vector_clock)


        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error: ' + str(e))
            return transaction_ver.VerifyTransactionResponse(is_valid=False,
                                                                      error_message='Error: ' + str(e),
                                                                      vector_clock=request.vector_clock)

# # Create a class to define the server functions, derived from
# # fraud_detection_pb2_grpc.HelloServiceServicer
# class HelloService(transaction_ver_grpc.HelloServiceServicer):
#     # Create an RPC function to say hello
#     def SayHello(self, request, context):
#         # Create a HelloResponse object
#         response = transaction_ver.HelloResponse()
#         # Set the greeting field of the response object
#         response.greeting = "Hello, " + request.name
#         # Print the greeting message
#         print(response.greeting)
#         # Return the response object
#         return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add ransactionVerificationService
    transaction_ver_grpc.add_TransactionVerificationServiceServicer_to_server(TransactionVerificationService(), server)
    # Listen on port 50052
    port = "50052"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print(">> Server started. Listening on port 50052.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()