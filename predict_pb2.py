# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: predict.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rpredict.proto\x12\x07predict\"\x07\n\x05\x45mpty\"\xb5\x02\n\x07Predict\x12\x13\n\x06symbol\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x19\n\x0c\x61\x63tual_price\x18\x02 \x01(\x02H\x01\x88\x01\x01\x12\x1c\n\x0fpredicted_price\x18\x03 \x01(\x02H\x02\x88\x01\x01\x12\x11\n\x04\x64\x61te\x18\x04 \x01(\x03H\x03\x88\x01\x01\x12\x1c\n\x0fstop_loss_price\x18\x05 \x01(\x02H\x04\x88\x01\x01\x12\x15\n\x08position\x18\x06 \x01(\tH\x05\x88\x01\x01\x12!\n\x14\x61vg_7_day_prediction\x18\x07 \x01(\x02H\x06\x88\x01\x01\x42\t\n\x07_symbolB\x0f\n\r_actual_priceB\x12\n\x10_predicted_priceB\x07\n\x05_dateB\x12\n\x10_stop_loss_priceB\x0b\n\t_positionB\x17\n\x15_avg_7_day_prediction\"\x82\x02\n\x0fPredictResponse\x12\x11\n\x04\x64\x61te\x18\x01 \x01(\tH\x00\x88\x01\x01\x12!\n\x07symbols\x18\x02 \x03(\x0b\x32\x10.predict.Predict\x12\x17\n\ncreated_at\x18\x03 \x01(\tH\x01\x88\x01\x01\x12\x16\n\tdelete_at\x18\x04 \x01(\tH\x02\x88\x01\x01\x12\x10\n\x03_id\x18\x05 \x01(\tH\x03\x88\x01\x01\x12\x17\n\nstatusCode\x18\x06 \x01(\tH\x04\x88\x01\x01\x12\x14\n\x07message\x18\x07 \x01(\tH\x05\x88\x01\x01\x42\x07\n\x05_dateB\r\n\x0b_created_atB\x0c\n\n_delete_atB\x06\n\x04X_idB\r\n\x0b_statusCodeB\n\n\x08_message\"!\n\x0cTimeStampReq\x12\x11\n\ttimeStamp\x18\x01 \x01(\x03\x32\x91\x02\n\x0ePredictService\x12+\n\x07predict\x12\x0e.predict.Empty\x1a\x0e.predict.Empty\"\x00\x12\x34\n\tdeleteall\x12\x15.predict.TimeStampReq\x1a\x0e.predict.Empty\"\x00\x12*\n\x06update\x12\x0e.predict.Empty\x1a\x0e.predict.Empty\"\x00\x12\x32\n\x04plot\x12\x0e.predict.Empty\x1a\x18.predict.PredictResponse\"\x00\x12<\n\x07getData\x12\x15.predict.TimeStampReq\x1a\x18.predict.PredictResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'predict_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_EMPTY']._serialized_start=26
  _globals['_EMPTY']._serialized_end=33
  _globals['_PREDICT']._serialized_start=36
  _globals['_PREDICT']._serialized_end=345
  _globals['_PREDICTRESPONSE']._serialized_start=348
  _globals['_PREDICTRESPONSE']._serialized_end=606
  _globals['_TIMESTAMPREQ']._serialized_start=608
  _globals['_TIMESTAMPREQ']._serialized_end=641
  _globals['_PREDICTSERVICE']._serialized_start=644
  _globals['_PREDICTSERVICE']._serialized_end=917
# @@protoc_insertion_point(module_scope)
