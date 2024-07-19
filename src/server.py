import grpc
from concurrent import futures
import time
import predict_pb2
import predict_pb2_grpc

class PredictServiceServicer(predict_pb2_grpc.PredictServiceServicer):
    def predict(self, request, context):
        return predict_pb2.Empty()  # implement this method
    
    def deleteall(self, request, context):
        return predict_pb2.Empty()  # implement this method
    
    def update(self, request, context):
        return predict_pb2.Empty()  # implement this method
    
    def plot(self, request, context):
        response = predict_pb2.PredictResponse()
        # Add some dummy data for demonstration
        response.predict.add(symbol="AAPL", date=1625155200, current_price=145.09, predicted_price=148.30)
        return response
    
    def getData(self, request, context):
        response = predict_pb2.PredictResponse()
        # Add some dummy data for demonstration
        response.predict.add(symbol="GOOG", date=1625241600, current_price=2500.00, predicted_price=2550.00)
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    predict_pb2_grpc.add_PredictServiceServicer_to_server(PredictServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
