import json
import grpc
from concurrent import futures
from datetime import datetime, timedelta
from pymongo import MongoClient
import redis
from src.config.redis import RedisService
from src.config.connectDb import connect_to_mongodb
from src.model.aiload import CryptoPricePredictor
import predict_pb2
import predict_pb2_grpc
import os

class PredictServiceServicer(predict_pb2_grpc.PredictServiceServicer):
    def __init__(self):
        self.api_key = (os.getenv("API_KEY"))
        self.api_secret = (os.getenv("SECRET_KEY"))
        self.model_path = './src/model/crypto_price_prediction_model.h5'
        self.crypto_predictor = CryptoPricePredictor(self.model_path, self.api_key, self.api_secret)
        self.db = connect_to_mongodb()
        self.redisService = RedisService()

    def predict(self, request, context):
        try:
            coin_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                            'DOTUSDT', 'SOLUSDT', 'DOGEUSDT', 'LTCUSDT', 'LINKUSDT']
            
            # Fetch predictions
            predictions = self.crypto_predictor.fetch_and_predict(coin_symbols)
            
            # Debugging: Print predictions
            print(f"Predictions received: {predictions}")

            # Check if predictions is None or not a list
            if predictions is None:
                raise ValueError("Predictions returned by fetch_and_predict are None")
            if not isinstance(predictions, list):
                raise ValueError(f"Predictions should be a list, got {type(predictions)}")

            # Debugging: Check each prediction
            for prediction in predictions:
                if not isinstance(prediction, dict):
                    raise ValueError(f"Invalid prediction format: {prediction}")
            
            # Save predictions to MongoDB
            collection = self.db["aipredict"]
            collection.insert_many(predictions)
            # self.redisService.setKey("testredis", json.dumps(predictions))
            
            return predict_pb2.Empty()
        except Exception as e:
            # Print exception details for debugging
            print(f"Exception occurred: {e}")
            context.set_details(f"Internal server error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return predict_pb2.Empty()

    def deleteall(self, request, context):
        try:
            # คูณค่าที่ได้รับด้วย 1000 เพื่อแปลงกลับเป็น milliseconds
            timestamp_in_ms = request.timeStamp * 1000

            # แปลง timestamp เป็น datetime object
            dt_obj = datetime.fromtimestamp(timestamp_in_ms / 1000)
            date_only = dt_obj.date()
            start_of_day = datetime.combine(date_only, datetime.min.time())
            end_of_day = datetime.combine(date_only, datetime.max.time())

            # ลบข้อมูลใน MongoDB ที่ตรงกับช่วงเวลานั้น
            result = self.db["aipredict"].delete_many({
                "created_at": {"$gte": start_of_day, "$lt": end_of_day}
            })
            print(f"Deleted {result.deleted_count} documents.")
            return predict_pb2.Empty()
        except Exception as e:
            print(f"Exception occurred during deleteall: {e}")
            context.set_details(f"Internal server error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return predict_pb2.Empty()


    def update(self, request, context):
        try:
            dt_obj = datetime.fromtimestamp(request.timeStamp)
            date_only = dt_obj.date()
            start_of_day = datetime.combine(date_only, datetime.min.time())
            end_of_day = datetime.combine(date_only, datetime.max.time())
            documents = self.db["aipredict"].find({
                "date": {"$gte": start_of_day, "$lt": end_of_day}
            })
            for doc in documents:
                self.db["aipredict"].update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"actual_price": doc.get("current_price", 0.0), "updated_at": datetime.utcnow()}}
                )
            return predict_pb2.Empty()
        except Exception as e:
            print(f"Exception occurred during update: {e}")
            context.set_details(f"Internal server error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return predict_pb2.Empty()
        
    def plot(self, request, context):
        try:
            response = predict_pb2.PredictResponse()
            for doc in self.db["aipredict"].find():
                response.predict.add(
                    symbol=doc.get("symbol", ""),
                    date=int(doc["date"].timestamp()) if isinstance(doc.get("date"), datetime) else doc.get("date"),
                    current_price=doc.get("current_price", 0.0),
                    predicted_price=doc.get("predicted_price", 0.0)
                )
            return response
        except Exception as e:
            print(f"Exception occurred during plot: {e}")
            context.set_details(f"Internal server error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return predict_pb2.PredictResponse()

    def getData(self, request, context):
        try:
            today = datetime.utcnow().date()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())
            documents = self.db["aipredict"].find({
                "created_at": {"$gte": start_of_day, "$lt": end_of_day},
                
            })
            print("Retrieved documents for symbol 'BTC':")
            response = predict_pb2.PredictResponse()
            for doc in documents:
                print(doc)
                response.predict.add(
                    symbol=doc.get("symbol", ""),
                    date=int(doc["date"].timestamp()) if isinstance(doc.get("date"), datetime) else doc.get("date"),
                    current_price=doc.get("current_price", 0.0),
                    predicted_price=doc.get("predicted_price", 0.0)
                )
            return response
        except Exception as e:
            print(f"Exception occurred during getData: {e}")
            context.set_details(f"Internal server error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return predict_pb2.PredictResponse()

# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     predict_pb2_grpc.add_PredictServiceServicer_to_server(PredictServiceServicer(), server)
#     server.add_insecure_port('[::]:50051')
#     print("Starting gRPC server on port 50051...")
#     server.start()
#     server.wait_for_termination()

# if __name__ == '__main__':
#     serve()
