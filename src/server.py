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

class PredictServiceServicer(predict_pb2_grpc.PredictServiceServicer) :
    def __init__(self):
        self.api_key = (os.getenv("API_KEY"))
        self.api_secret = (os.getenv("SECRET_KEY"))
        self.model_path = './src/model/crypto_price_prediction_model.h5'
        self.crypto_predictor = CryptoPricePredictor(self.model_path, self.api_key, self.api_secret)
        self.db = connect_to_mongodb()
        self.redisService = RedisService()
        self.exchange = getattr(ccxt, "binance")()

    def predict(self, request, context):
        try:
            coin_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                            'DOTUSDT', 'SOLUSDT', 'DOGEUSDT', 'LTCUSDT', 'LINKUSDT']
            
            # Fetch predictions
            predictions = self.crypto_predictor.fetch_and_predict(coin_symbols)
            
            # Debugging: Print predictions
            print(f"Predictions received: {predictions}")

            # # Check if predictions is None or not a list
            # if predictions is None:
            #     raise ValueError("Predictions returned by fetch_and_predict are None")
            # if not isinstance(predictions, list):
            #     raise ValueError(f"Predictions should be a list, got {type(predictions)}")

            # # Debugging: Check each prediction
            # for prediction in predictions:
            #     if not isinstance(prediction, dict):
            #         raise ValueError(f"Invalid prediction format: {prediction}")
            
            # Save predictions to MongoDB
            collection = self.db["aipredict"]
            collection.insert_one(predictions)
            # self.redisService.setKey("testredis", json.dumps(predictions))
            
            return predict_pb2.Empty()
        except Exception as e:
            # Print exception details for debugging
            print(f"Exception occurred: {e}")
            context.set_details(f"Internal server error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return predict_pb2.Empty()

    # ของทดสอบวันที


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
            # กำหนดวันที่เมื่อวานและเวลา 7 โมงเช้า
            yesterday = datetime.utcnow().date() - timedelta(days=1)
            yesterday_at_7am = datetime.combine(yesterday, datetime.min.time()) + timedelta(hours=7)
            yesterday_at_7am_str = yesterday_at_7am.strftime('%Y-%m-%d %H:%M:%S')

            # Debugging: พิมพ์วันที่และเวลาของเมื่อวานเวลา 7 โมงเช้า
            print(f"Yesterday's date and time : {yesterday_at_7am_str}")

            # ค้นหาเอกสารใน MongoDB ที่ตรงกับวันที่เมื่อวานเวลา 7 โมงเช้า
            document = self.db["aipredict"].find_one({"date": yesterday_at_7am_str})

            if document:
                updated_symbols = []
                for symbol_data in document['symbols']:
                    # อัปเดต actual_price ด้วยราคาทำนายจากเมื่อวาน (predicted_price)
                    symbol_data['actual_price'] = symbol_data["predicted_price"]
                    updated_symbols.append(symbol_data)

                # อัปเดตเอกสารใน MongoDB ด้วยข้อมูลใหม่
                self.db["aipredict"].find_one_and_update(
                    {"_id": document['_id']},
                    {"$set": {"symbols": updated_symbols}},
                    return_document=True  # คืนค่าเอกสารที่ถูกอัปเดต
                )

                print(f"Document with _id: {document['_id']} updated successfully.")
            else:
                print("No document found with the specified criteria.")

            return predict_pb2.Empty()

        except Exception as e:
            print(f"Exception occurred during update: {e}")
            context.set_details(f"Internal server error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return predict_pb2.PredictResponse(statusCode="500", message=f"Internal server error: {e}")


    def getData(self, request, context):
        try:
            today = datetime.utcnow().date()
            print(f"Querying data for date: {today}")

            document = self.db["aipredict"].find_one({
                "created_at": today.strftime('%Y-%m-%d')
            })

            response = predict_pb2.PredictResponse()

            if document:
                try:
                    # print(f"Processing document: {document}") 
                    response.date = document.get('created_at')
                    
                    for symbol_data in document.get("symbols", []):
                        response.symbols.add(
                            symbol=symbol_data.get("symbol", ""),
                            predicted_price=symbol_data.get("predicted_price", 0.0),
                            # actual_price=symbol_data.get("actual_price", 0.0)  # Ensure this line is included
                        )
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

            # today = datetime.utcnow().date()
            # start_of_day = datetime.combine(today, datetime.min.time())
            # end_of_day = datetime.combine(today, datetime.max.time())
            # documents = self.db["aipredict"].find({
            #     "created_at": {"$gte": start_of_day, "$lt": end_of_day},
                
            # })
            # print("Retrieved documents for symbol 'BTC':")
            # response = predict_pb2.PredictResponse()
            # for doc in documents:
            #     print(doc)
            #     response.predict.add(
            #         symbol=doc.get("symbol", ""),
            #         date=int(doc["date"].timestamp()) if isinstance(doc.get("date"), datetime) else doc.get("date"),
            #         current_price=doc.get("current_price", 0.0),
            #         predicted_price=doc.get("predicted_price", 0.0)
            #     )
            # return response
        # except Exception as e:
        #     print(f"Exception occurred during getData: {e}")
        #     context.set_details(f"Internal server error: {e}")
        #     context.set_code(grpc.StatusCode.INTERNAL)
        #     return predict_pb2.PredictResponse()
