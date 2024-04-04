import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, utils_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

import grpc
from concurrent import futures

class FraudDetectionService(fraud_detection_grpc.FraudDetectionServiceServicer):
    def FraudDetection(self, request, context):
        print(f"Fraud detection service called. {request.vector_clock}")
        request.vector_clock.clock['fraud_detection'] += 1
        response = fraud_detection.FraudResponse()
        if request.total_qty > 1000:
            response.is_valid = False
            response.message = "Transaction is fraud"

        else:
            response.is_valid = True
            response.message = "Transaction is valid"

        print(response.message)
        response = fraud_detection.FraudResponse(is_valid=response.is_valid, message=response.message,
                                                 vector_clock=fraud_detection.VectorClock(
                                                     clock=request.vector_clock.clock))
        print(f"Fraud detection response: {response}")
        return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    fraud_detection_grpc.add_FraudDetectionServiceServicer_to_server(FraudDetectionService(), server)
    # Listen on port 50051
    port = "50051"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("Server started. Listening on port 50051.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()