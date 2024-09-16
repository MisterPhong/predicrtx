import json
import ccxt
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
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("SECRET_KEY")
        self.model_path = './src/model/crypto_price_prediction_model.h5'
        self.crypto_predictor = CryptoPricePredictor(self.model_path, self.api_key, self.api_secret)
        self.db = connect_to_mongodb()
        self.redisService = RedisService()
        self.exchange = getattr(ccxt, "binance")()

    def predict(self, request, context):
        try:
            coin_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                            'DOTUSDT', 'SOLUSDT', 'DOGEUSDT', 'LTCUSDT', 'LINKUSDT']
            
            # Fetch and update predictions
            predictions = self.crypto_predictor.update(coin_symbols)
            
            # Debugging: Print predictions
            print(f"Predictions received: {predictions}")
            
            # Save predictions to MongoDB
            collection = self.db["aipredict"]
            collection.insert_one(predictions)
            
            return predict_pb2.Empty()
        except Exception as e:
            print(f"Exception occurred: {e}")
            context.set_details(f"Internal server error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return predict_pb2.Empty()
    
    def deleteall(self, request, context):
        try:
            # Convert timestamp to milliseconds
            timestamp_in_ms = request.timeStamp * 1000

            # Convert timestamp to datetime object
            dt_obj = datetime.fromtimestamp(timestamp_in_ms / 1000)
            date_only = dt_obj.date()
            start_of_day = datetime.combine(date_only, datetime.min.time())
            end_of_day = datetime.combine(date_only, datetime.max.time())

            # Delete documents in MongoDB for the given date
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
        
    def getData(self, request, context):
        try:
            today = datetime.utcnow().date()
            print(f"Querying data for date: {today}")

            document = self.db["aipredict"].find_one({
                "date": today.strftime('%Y-%m-%d')  # Adjust query to match the date format in MongoDB
            })

            response = predict_pb2.PredictResponse()

            if document:
                try:
                    response.date = document.get('date')
                    
                    for symbol_data in document.get("symbols", []):
                        symbol_entry = response.symbols.add()
                        symbol_entry.symbol = symbol_data.get("symbol", "")
                        symbol_entry.predicted_price = symbol_data.get("predicted_price", 0.0)
                        symbol_entry.actual_price = symbol_data.get("actual_price", 0.0)
                        symbol_entry.position = symbol_data.get("position", "")
                        symbol_entry.stop_loss_price = symbol_data.get("stop_loss_price", 0.0)
                        symbol_entry.avg_7_day_prediction = symbol_data.get("avg_7_day_prediction", 0.0)
                except Exception as e:
                    print(f"Error processing document: {e}")
                    return predict_pb2.PredictResponse(statusCode="500", message=f"Error processing document: {e}")
            else:
                print("No document found")
                return predict_pb2.PredictResponse(statusCode="404", message="No document found for today's date.")

            print(f"Document processed: {bool(document)}")
            return response

        except Exception as e:
            print(f"Exception occurred during getData: {e}")
            context.set_details(f"Internal server error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return predict_pb2.PredictResponse(statusCode="500", message=f"Internal server error: {e}")
