# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: order_queue.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11order_queue.proto\x12\norderqueue\"*\n\x05Order\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x10\n\x08userName\x18\x02 \x01(\t\"2\n\x0e\x45nqueueRequest\x12 \n\x05order\x18\x01 \x01(\x0b\x32\x11.orderqueue.Order\"3\n\x0f\x45nqueueResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2S\n\x11OrderQueueService\x12>\n\x0c\x45nqueueOrder\x12\x11.orderqueue.Order\x1a\x1b.orderqueue.EnqueueResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'order_queue_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_ORDER']._serialized_start=33
  _globals['_ORDER']._serialized_end=75
  _globals['_ENQUEUEREQUEST']._serialized_start=77
  _globals['_ENQUEUEREQUEST']._serialized_end=127
  _globals['_ENQUEUERESPONSE']._serialized_start=129
  _globals['_ENQUEUERESPONSE']._serialized_end=180
  _globals['_ORDERQUEUESERVICE']._serialized_start=182
  _globals['_ORDERQUEUESERVICE']._serialized_end=265
# @@protoc_insertion_point(module_scope)
