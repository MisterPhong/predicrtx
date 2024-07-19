#! /bin/bash

py -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./proto/predict.proto