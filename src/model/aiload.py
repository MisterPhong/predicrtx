import numpy as np
import pandas as pd
from binance.client import Client
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta, date

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

    def preprocess_data(self, data, ema_period=15):
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
        tomorrow_morning = datetime.combine(date.today() + timedelta(days=1), datetime.min.time()).replace(hour=7).strftime('%Y-%m-%d %H:%M:%S')

        payload = {
            "date": tomorrow_morning,
            "symbols": [],
            'created_at': date.today().strftime('%Y-%m-%d'),  # Convert to string
            'delete_at': None
        }

        for symbol in coin_symbols:
            crypto_data = self.get_crypto_data(symbol, interval='1d', limit=365)
            crypto_data = self.preprocess_data(crypto_data, ema_period=20)
            predicted_price = self.predict_price(crypto_data)
        
            result = {
                'symbol': symbol,
                'predicted_price': float(predicted_price),
            }

            # Append the result to the symbols array in the payload
            payload['symbols'].append(result)

        return payload


