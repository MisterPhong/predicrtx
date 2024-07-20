import grpc
from concurrent import futures
import time
import predict_pb2
import predict_pb2_grpc
from src.server import PredictServiceServicer 

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
