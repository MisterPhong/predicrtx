import grpc
from concurrent import futures
import time
from proto import ProtoType
from pymongo import MongoClient
import datetime
from model.aiload import CryptoPricePredictor
import predict_pb2_grpc
import predict_pb2

class PredictService(predict_pb2_grpc.PredictService):
    def __init__(self,model_path, api_key, api_secret):
        self.client = MongoClient("mongodb://root:example@localhost:27017/")
        self.db = self.client["crypto_predictions"]
        self.collection = self.db["crypto_predict"]
        self.crypto_predictor = CryptoPricePredictor(model_path, api_key, api_secret)


    def predict(self, request, context):        
        coin_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                    'DOTUSDT', 'SOLUSDT', 'DOGEUSDT', 'LTCUSDT', 'LINKUSDT',
                    'MATICUSDT', 'UNIUSDT', 'ICPUSDT', 'VETUSDT', 'XLMUSDT',
                    'FILUSDT', 'TRXUSDT', 'AAVEUSDT', 'EOSUSDT', 'THETAUSDT']
        print(self.crypto_predictor.fetch_and_predict(coin_symbols))
        # predictions = []
        # for doc in self.collection.find():
        #     timestamp = int(doc["Date"].timestamp()) if isinstance(doc["Date"], datetime.datetime) else doc["Date"]
            
        #     prediction = predict_pb2.Predict(
        #         symbol=doc["Symbol"],
        #         date=timestamp,
        #         current_price=doc["Current Price"],
        #         predicted_price=doc["Predicted Price"]
        #     )
        #     predictions.append(prediction)
        return predict_pb2.PredictResponse({})
    
    def deleteall(self, request, context):
        for doc in self.collection.find():
            timestamp = int(doc["Date"].timestamp()) if isinstance(doc["Date"], datetime.datetime) else doc["Date"]

            return predict_pb2.TimeStampReq()
        
    def update():

        return predict_pb2.TimeStampReq()

    def plot():

        return predict_pb2.Empty()
        
    def getData():

        return predict_pb2.TimeStampReq()

