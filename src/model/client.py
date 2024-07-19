import grpc
import predict_pb2
import predict_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = predict_pb2_grpc.PredictServiceStub(channel)
        response = stub.Predict(predict_pb2.Empty())
        for prediction in response.predict:
            print(f"Symbol: {prediction.symbol}, Date: {prediction.date}, Current Price: {prediction.current_price}, Predicted Price: {prediction.predicted_price}")

if __name__ == '__main__':
    run()
