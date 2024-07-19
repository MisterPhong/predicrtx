import grpc
import predict_pb2
import predict_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = predict_pb2_grpc.PredictServiceStub(channel)
        
        # Call predict method
        response = stub.predict(predict_pb2.Empty())
        print("Predict response: ", response)
        
        # Call plot method
        response = stub.plot(predict_pb2.Empty())
        print("Plot response: ", response)

        # Call getData method
        timestamp_request = predict_pb2.TimeStampReq(timeStamp=1625241600)
        response = stub.getData(timestamp_request)
        print("GetData response: ", response)

if __name__ == '__main__':
    run()
