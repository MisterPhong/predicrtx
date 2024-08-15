import grpc
from concurrent import futures
import time
import predict_pb2
import predict_pb2_grpc
from src.server import PredictServiceServicer 
from dotenv import load_dotenv
import os

# โหลดตัวแปรสภาพแวดล้อมจากไฟล์ .env
load_dotenv()
port = os.getenv("PORT")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    predict_pb2_grpc.add_PredictServiceServicer_to_server(PredictServiceServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    print("Starting_openup")
    print(f"server run on port: {port}")
    serve()
