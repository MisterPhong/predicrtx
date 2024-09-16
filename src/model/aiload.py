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
        predicted_price = self.price_scaler.inverse_transform(predictions).flatten()[0]

        # Apply a larger divergence factor
        divergence_factor = np.random.uniform(0.98, 1.02)  # Change range to control divergence
        adjusted_predicted_price = predicted_price * divergence_factor

        return adjusted_predicted_price

    def predict_7_days_average(self, data, time_step=30):
        prediction_data = data[['price', 'price_ema']]
        scaled_data = self.scaler.fit_transform(prediction_data)
        self.price_scaler.fit(prediction_data[['price']])

        last_30_days_scaled = scaled_data[-time_step:]
        X_future = np.expand_dims(last_30_days_scaled, axis=0)

        predicted_prices = []
        for day in range(7):
            predictions = self.model.predict(X_future)
            predicted_price = self.price_scaler.inverse_transform(predictions).flatten()[0]
            predicted_prices.append(predicted_price)

            # Update the future prediction data for the next day
            new_day_scaled = np.array([self.scaler.transform([[predicted_price, predicted_price]])[0]])
            X_future = np.concatenate((X_future[:, 1:], new_day_scaled.reshape(1, 1, -1)), axis=1)

        avg_7_day_price = np.mean(predicted_prices)
        return avg_7_day_price
    
    def update(self, coin_symbols):
        payload = {
            "date": date.today().strftime('%Y-%m-%d'),
            "symbols": []
        }

        for symbol in coin_symbols:
            # Fetch the current price of yesterday
            yesterday_data = self.get_crypto_data(symbol, interval='1d', limit=2)
            if len(yesterday_data) < 2:
                continue  # Skip if there's not enough data

            yesterday_price = yesterday_data['price'].iloc[-2]  # Price of the day before

            # Fetch today's data and perform predictions
            crypto_data = self.get_crypto_data(symbol, interval='1d', limit=30)
            crypto_data = self.preprocess_data(crypto_data, ema_period=15)
            
            predicted_price = self.predict_price(crypto_data)
            avg_7_day_prediction = self.predict_7_days_average(crypto_data)
            current_price = crypto_data['price'].iloc[-1]

            stop_loss_price = current_price * 0.98
            position = 'Long' if predicted_price > current_price else 'Short'

            result = {
                'symbol': symbol,
                'predicted_price': float(predicted_price),
                'avg_7_day_prediction': float(avg_7_day_prediction),
                'stop_loss_price': float(stop_loss_price),
                'position': position,
                'actual_price': float(yesterday_price)  # Add actual price from yesterday
            }

            payload['symbols'].append(result)

        return payload

    def fetch_and_predict(self, coin_symbols):
        tomorrow_morning = datetime.combine(date.today() + timedelta(days=1), datetime.min.time()).replace(hour=7).strftime('%Y-%m-%d %H:%M:%S')

        payload = {
            "date": tomorrow_morning,
            "symbols": [],
            'created_at': date.today().strftime('%Y-%m-%d'),
            'delete_at': None
        }

        for symbol in coin_symbols:
            crypto_data = self.get_crypto_data(symbol, interval='1d', limit=30)
            crypto_data = self.preprocess_data(crypto_data, ema_period=15)
            
            # ตรวจสอบข้อมูลที่เตรียมไว้สำหรับการพยากรณ์
            print(f"Preprocessed data for {symbol}:")
            print(crypto_data.tail())  # ดูข้อมูลล่าสุด
            
            predicted_price = self.predict_price(crypto_data)
            avg_7_day_prediction = self.predict_7_days_average(crypto_data)
            current_price = crypto_data['price'].iloc[-1]

            stop_loss_price = current_price * 0.98

            position = 'Long' if predicted_price > current_price else 'Short'

            result = {
                'symbol': symbol,
                'predicted_price': float(predicted_price),
                'avg_7_day_prediction': float(avg_7_day_prediction),
                'stop_loss_price': float(stop_loss_price),
                'position': position,
            }

            payload['symbols'].append(result)

        return payload
