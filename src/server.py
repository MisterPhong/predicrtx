import grpc
from concurrent import futures
import time

from pymongo import MongoClient
from src.config.connectDb import connect_to_mongodb
from src.model.aiload import CryptoPricePredictor
import predict_pb2
import predict_pb2_grpc

class PredictServiceServicer(predict_pb2_grpc.PredictServiceServicer):
    def __init__(self):
        self.api_key = "ZIIJYaRgR9WyJaKxq7zVehOtkfomjyX29NwNLWLlBgE3ikw5jtkMxVQD0IgewUxQ"
        self.api_secret = " 7JmVNUuzOSyjzDnzGsewBIszScuj47sf1w7MRNDUaRj8pE49gAX4fsgP9RlDCi6S"
        self.model_path = './src/model/crypto_price_prediction_model.h5'
        # self.client = MongoClient("mongodb://root:example@localhost:27017/")
        # self.db = self.client["crypto_predictions"]
        # self.collection = self.db["crypto_predict"]
        self.crypto_predictor = CryptoPricePredictor(self.model_path, self.api_key, self.api_secret)
        self.db = connect_to_mongodb()
        

    def predict(self, request, context):
        coin_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                        'DOTUSDT', 'SOLUSDT', 'DOGEUSDT', 'LTCUSDT', 'LINKUSDT',
                        'MATICUSDT', 'UNIUSDT', 'ICPUSDT', 'VETUSDT', 'XLMUSDT',
                        'FILUSDT', 'TRXUSDT', 'AAVEUSDT', 'EOSUSDT', 'THETAUSDT']
      
        predictions = self.crypto_predictor.fetch_and_predict(coin_symbols)
        # Add code to save predictions to MongoDB if needed
        collection = self.db["aipredict"]
      
        collection.insert_many(predictions)

        return predict_pb2.Empty()  # implement this method
    
    def deleteall(self, request, context):
        ### delete where วันที่
        return predict_pb2.Empty()  # implement this method
    
    def update(self, request, context):
        ### upadate where เมื่อวาน
        return predict_pb2.Empty()  # implement this method
    
    def plot(self, request, context):
        response = predict_pb2.PredictResponse()
        # Find All
        response.predict.add(symbol="AAPL", date=1625155200, current_price=145.09, predicted_price=148.30)
        return response
    
    def getData(self, request, context):
        response = predict_pb2.PredictResponse()
        # Q ry where today
        response.predict.add(symbol="GOOG", date=1625241600, current_price=2500.00, predicted_price=2550.00)
        return response

# from datetime import datetime
# from pymongo import MongoClient
# from src.model.aiload import CryptoPricePredictor
# import predict_pb2
# import predict_pb2_grpc

# class PredictServiceServicer(predict_pb2_grpc.PredictServiceServicer):
#     def __init__(self):
#         self.api_key = "ZIIJYaRgR9WyJaKxq7zVehOtkfomjyX29NwNLWLlBgE3ikw5jtkMxVQD0IgewUxQ"
#         self.api_secret = " 7JmVNUuzOSyjzDnzGsewBIszScuj47sf1w7MRNDUaRj8pE49gAX4fsgP9RlDCi6S"
#         self.model_path = './src/model/crypto_price_prediction_model.h5'
#         self.client = MongoClient("mongodb://root:example@localhost:27017/")
#         self.db = self.client["crypto_predictions"]
#         self.collection = self.db["crypto_predict"]
#         self.crypto_predictor = CryptoPricePredictor(self.model_path, self.api_key, self.api_secret)


#     def predict(self, request, context):
#         coin_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
#                         'DOTUSDT', 'SOLUSDT', 'DOGEUSDT', 'LTCUSDT', 'LINKUSDT',
#                         'MATICUSDT', 'UNIUSDT', 'ICPUSDT', 'VETUSDT', 'XLMUSDT',
#                         'FILUSDT', 'TRXUSDT', 'AAVEUSDT', 'EOSUSDT', 'THETAUSDT']
#         # Example: Fetch and predict prices for the given symbols
#         predictions = self.crypto_predictor.fetch_and_predict(coin_symbols)
#         # Add code to save predictions to MongoDB if needed
#         print("Hello")
#         return predict_pb2.PredictResponse(predict=predictions)

    
#     def deleteall(self, request, context):
#         self.collection.delete_many({})
#         return predict_pb2.Empty()
    
#     def update(self, request, context):
#         # Implement update logic if needed
#         return predict_pb2.Empty()
    
#     def plot(self, request, context):
#         predictions = []
#         for doc in self.collection.find():
#             timestamp = int(doc["Date"].timestamp()) if isinstance(doc["Date"], datetime.datetime) else doc["Date"]
#             prediction = predict_pb2.Predict(
#                 symbol=doc["Symbol"],
#                 date=timestamp,
#                 current_price=doc["Current Price"],
#                 predicted_price=doc["Predicted Price"]
#             )
#             predictions.append(prediction)
#         return predict_pb2.PredictResponse(predict=predictions)
    
#     def getData(self, request, context):
#         predictions = []
#         for doc in self.collection.find({"Date": request.timeStamp}):
#             prediction = predict_pb2.Predict(
#                 symbol=doc["Symbol"],
#                 date=int(doc["Date"].timestamp()) if isinstance(doc["Date"], datetime.datetime) else doc["Date"],
#                 current_price=doc["Current Price"],
#                 predicted_price=doc["Predicted Price"]
#             )
#             predictions.append(prediction)
#         return predict_pb2.PredictResponse(predict=predictions)