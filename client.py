import grpc
import predict_pb2
import predict_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = predict_pb2_grpc.PredictServiceStub(channel)

        # Example call to the predict method
        print("Calling predict method")
        try:
            response = stub.predict(predict_pb2.Empty())
            print("Predict response received")
        except grpc.RpcError as e:
            print(f"Error calling predict method: {e}")

        # Example call to the deleteall method
        print("Calling deleteall method")
        try:
            response = stub.deleteall(predict_pb2.TimeStampReq(timeStamp=1658937600))
            print("Deleteall response received")
        except grpc.RpcError as e:
            print(f"Error calling deleteall method: {e}")

        # Example call to the update method
        print("Calling update method")
        try:
            response = stub.update(predict_pb2.TimeStampReq(timeStamp=1658937600))
            print("Update response received")
        except grpc.RpcError as e:
            print(f"Error calling update method: {e}")

        # Example call to the plot method
        print("Calling plot method")
        try:
            response = stub.plot(predict_pb2.Empty())
            print("Plot response received")
            for prediction in response.predict:
                print(f"Symbol: {prediction.symbol}, Date: {prediction.date}, Current Price: {prediction.current_price}, Predicted Price: {prediction.predicted_price}")
        except grpc.RpcError as e:
            print(f"Error calling plot method: {e}")

        # Example call to the getData method
        print("Calling getData method")
        try:
            response = stub.getData(predict_pb2.TimeStampReq(timeStamp=1658937600))
            print("GetData response received")
            for prediction in response.predict:
                print(f"Symbol: {prediction.symbol}, Date: {prediction.date}, Current Price: {prediction.current_price}, Predicted Price: {prediction.predicted_price}")
        except grpc.RpcError as e:
            print(f"Error calling getData method: {e}")

if __name__ == '__main__':
    run()
