import numpy as np
import pandas as pd
from binance.client import Client
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta

class CryptoPricePredictor:
    def __init__(self, model_path, api_key, api_secret):
        self.model = load_model(model_path)
        self.client = Client(api_key, api_secret)
        self.scaler = MinMaxScaler()
        self.price_scaler = MinMaxScaler()

    def get_crypto_data(self, coin_symbol, interval='1d', limit=365):
        interval_map = {
            '1d': Client.KLINE_INTERVAL_1DAY,
            '1h': Client.KLINE_INTERVAL_1HOUR,
            '1m': Client.KLINE_INTERVAL_1MINUTE
        }

        interval = interval_map.get(interval)
        if not interval:
            raise ValueError("Invalid interval. Use '1d', '1h', or '1m'.")

        klines = self.client.get_historical_klines(coin_symbol, interval, f"{limit} day ago UTC")
        timestamps = [datetime.utcfromtimestamp(kline[0] / 1000) for kline in klines]
        prices = [float(kline[4]) for kline in klines]
        df = pd.DataFrame({'timestamp': timestamps, 'price': prices})
        return df

    def preprocess_data(self, data, ema_period=20):
        data['price_ema'] = data['price'].ewm(span=ema_period, adjust=False).mean()
        return data[['timestamp', 'price', 'price_ema']]

    def predict_price(self, data, time_step=30):
        prediction_data = data[['price', 'price_ema']]
        scaled_data = self.scaler.fit_transform(prediction_data)
        self.price_scaler.fit(prediction_data[['price']])

        last_30_days_scaled = scaled_data[-time_step:]
        X_future = np.expand_dims(last_30_days_scaled, axis=0)

        predictions = self.model.predict(X_future)
        predicted_price = self.price_scaler.inverse_transform(predictions)
        return predicted_price.flatten()[0]

    def fetch_and_predict(self, coin_symbols):
        results = []
        for symbol in coin_symbols:
            crypto_data = self.get_crypto_data(symbol, interval='1d', limit=365)
            crypto_data = self.preprocess_data(crypto_data, ema_period=20)
            predicted_price = self.predict_price(crypto_data)

            next_day_timestamp = crypto_data['timestamp'].iloc[-1] + timedelta(days=1)
            actual_price_data = self.get_crypto_data(symbol, interval='1d', limit=2)
            actual_price = actual_price_data[actual_price_data['timestamp'] == next_day_timestamp]['price'].values
            actual_price = actual_price[0] if len(actual_price) > 0 else np.nan

            last_timestamp = crypto_data['timestamp'].iloc[-1]
            next_day = last_timestamp + timedelta(days=1)
            current_price = crypto_data['price'].iloc[-1]
            current_time = datetime.utcnow()

            result = {
                'Symbol': symbol,
                'Date': next_day,
                'Time': next_day.strftime('%H:%M:%S'),
                'Current Price': current_price,
                'Predicted Price': predicted_price,
                'Actual Price': actual_price,
                'createdAt': current_time,
                'updatedAt': current_time
            }

            results.append(result)
        return results

# if __name__ == "__main__":
#     api_key = 'dhxyexgq56p8qfXIXdkL40DOTfpopgBysz8IEbvxJfuqksbDphNubGS8ydMFJTAI'
#     api_secret = 'nquFquj6eKLmvgWJ4Er6SlFYFte8b0auIKfFmKUH0A7Fh6Mg7FGKb97PPgZggXnO'
#     model_path = 'crypto_price_prediction_model.h5'
    
#     coin_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
#                     'DOTUSDT', 'SOLUSDT', 'DOGEUSDT', 'LTCUSDT', 'LINKUSDT',
#                     'MATICUSDT', 'UNIUSDT', 'ICPUSDT', 'VETUSDT', 'XLMUSDT',
#                     'FILUSDT', 'TRXUSDT', 'AAVEUSDT', 'EOSUSDT', 'THETAUSDT']
    
#     predictor = CryptoPricePredictor(model_path, api_key, api_secret)
#     results = predictor.fetch_and_predict(coin_symbols)
    
#     for result in results:
#         print(result)
