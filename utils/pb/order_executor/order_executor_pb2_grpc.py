# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import order_executor_pb2 as order__executor__pb2


class OrderExecutorServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Dequeue = channel.unary_unary(
                '/orderexecutor.OrderExecutorService/Dequeue',
                request_serializer=order__executor__pb2.DequeueRequest.SerializeToString,
                response_deserializer=order__executor__pb2.DequeueResponse.FromString,
                )
        self.Are_You_Available = channel.unary_unary(
                '/orderexecutor.OrderExecutorService/Are_You_Available',
                request_serializer=order__executor__pb2.Are_You_AvailableRequest.SerializeToString,
                response_deserializer=order__executor__pb2.Are_You_AvailableResponse.FromString,
                )


class OrderExecutorServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Dequeue(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Are_You_Available(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrderExecutorServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Dequeue': grpc.unary_unary_rpc_method_handler(
                    servicer.Dequeue,
                    request_deserializer=order__executor__pb2.DequeueRequest.FromString,
                    response_serializer=order__executor__pb2.DequeueResponse.SerializeToString,
            ),
            'Are_You_Available': grpc.unary_unary_rpc_method_handler(
                    servicer.Are_You_Available,
                    request_deserializer=order__executor__pb2.Are_You_AvailableRequest.FromString,
                    response_serializer=order__executor__pb2.Are_You_AvailableResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'orderexecutor.OrderExecutorService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class OrderExecutorService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Dequeue(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/orderexecutor.OrderExecutorService/Dequeue',
            order__executor__pb2.DequeueRequest.SerializeToString,
            order__executor__pb2.DequeueResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Are_You_Available(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/orderexecutor.OrderExecutorService/Are_You_Available',
            order__executor__pb2.Are_You_AvailableRequest.SerializeToString,
            order__executor__pb2.Are_You_AvailableResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
