import grpc
import predict_pb2
import predict_pb2_grpc
import time as t

def run():
    with grpc.insecure_channel('localhost:50057') as channel:
        stub = predict_pb2_grpc.PredictServiceStub(channel)
        
               # Call predict method
        try:
            response = stub.predict(predict_pb2.Empty())
            print("Predict response: ", response)
        except grpc.RpcError as e:
            print(f"gRPC error in predict: {e.code()} - {e.details()}")

        # #update method
        # try:
        #     response = stub.update(predict_pb2.TimeStampReq())
        #     print("Update response: ", response)
        # except grpc.RpcError as e:
        #     print(f"gRPC error in predict: {e.code()} - {e.details()}")
       

        # Call plot method
        # response = stub.plot(predict_pb2.Empty())
        # print("Plot response: ", response)

        # # Call getData method

        # Call getData method
        try:
            current_timestamp = int(t.time())  # Get the current timestamp in seconds
            timestamp_request = predict_pb2.TimeStampReq(timeStamp=int(current_timestamp / 1000))  # Convert to integer
            response = stub.getData(timestamp_request)
            print("GetData response: ", response)
        except grpc.RpcError as e:
            print(f"gRPC error in getData: {e.code()} - {e.details()}")


if __name__ == '__main__':
    run()
