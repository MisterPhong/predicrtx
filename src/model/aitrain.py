import numpy as np
from binance.client import Client
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping
from datetime import datetime, timedelta


# Function to create the dataset with a sliding window
def create_dataset(data, time_step=90):
    X, y = [], []
    for i in range(len(data) - time_step):
        a = data[i:(i + time_step)]
        X.append(a)
        y.append(data[i + time_step, 0])  # Predict the next day
    return np.array(X), np.array(y)

# Function to get crypto data from Binance API
def get_crypto_data(coin_symbol, interval='1d', limit=365):
    api_key = 'ZIIJYaRgR9WyJaKxq7zVehOtkfomjyX29NwNLWLlBgE3ikw5jtkMxVQD0IgewUxQ'
    api_secret = '7JmVNUuzOSyjzDnzGsewBIszScuj47sf1w7MRNDUaRj8pE49gAX4fsgP9RlDCi6S'
    client = Client(api_key, api_secret)

    interval_map = {
        '1d': Client.KLINE_INTERVAL_1DAY,
        '1h': Client.KLINE_INTERVAL_1HOUR,
        '1m': Client.KLINE_INTERVAL_1MINUTE
    }
    
    interval = interval_map.get(interval)
    if not interval:
        raise ValueError("Invalid interval. Use '1d', '1h', or '1m'.")

    klines = client.get_historical_klines(coin_symbol, interval, f"{limit} day ago UTC")
    timestamps = [datetime.utcfromtimestamp(kline[0] / 1000) for kline in klines]
    prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'timestamp': timestamps, 'price': prices})
    return df

# Function to preprocess data and add EMA values
def preprocess_data(data, ema_period=15):
    data['price_ema'] = data['price'].ewm(span=ema_period, adjust=False).mean()
    return data[['timestamp', 'price', 'price_ema']]

# Load data for each coin and concatenate
coin_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                'DOTUSDT', 'SOLUSDT', 'DOGEUSDT', 'LTCUSDT', 'LINKUSDT']
crypto_data_list = []
for coin in coin_symbols:
    coin_data = get_crypto_data(coin, interval='1d', limit=365)
    coin_data['coin_symbol'] = coin  # Add the coin symbol to the data
    crypto_data_list.append(coin_data)

# Combine all the data into one DataFrame
crypto_data = pd.concat(crypto_data_list, ignore_index=True)

# Add EMA values as features
ema_period = 15
crypto_data = preprocess_data(crypto_data, ema_period)

# Select features for prediction
prediction_data = crypto_data[['price', 'price_ema']]

# Normalize/Scale the input features
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(prediction_data)

# Create a separate scaler for the target variable (price)
price_scaler = MinMaxScaler()
price_scaler.fit(prediction_data[['price']])

# Create the dataset with the sliding window
time_step = 90  # Matching time_step in your prediction script
X, y = create_dataset(scaled_data, time_step)

# Ensure X has three dimensions (num_samples, time_step, num_features)
print(f"X shape before reshape: {X.shape}")

# No need to reshape as the create_dataset function returns X with correct shape
print(f"X shape after reshape: {X.shape}")

# Split the data into training and validation sets
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42)

# Function to build the LSTM model
def build_time_series_model(input_shape):
    model = keras.Sequential([
        layers.GRU(50, return_sequences=True, input_shape=input_shape),
        layers.GRU(25, return_sequences=False),
        layers.Dense(12.5),
        layers.Dense(1)
    ])
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.0001), loss='mean_squared_error')
    return model

# Ensure input_shape is correct
print(f"Input shape: {(time_step, X_train.shape[2])}")

model = build_time_series_model((time_step, X_train.shape[2]))

early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

history = model.fit(X_train, y_train, validation_data=(X_valid, y_valid), epochs=100, batch_size=16, callbacks=[early_stopping])

# Save the model for future predictions
model.save('crypto_price_predictor_modelx.h5')

# Prepare data for prediction (use the last 60 days of the training data)
last_60_days_scaled = scaled_data[-90:]  # Select the last 60 days
X_future = np.expand_dims(last_60_days_scaled, axis=0)

# Ensure X_future has three dimensions (num_samples, time_step, num_features)
print(f"X_future shape: {X_future.shape}")

# Make predictions
predictions = model.predict(X_future)

# Inverse scale the predictions using the target variable scaler
predicted_price = price_scaler.inverse_transform(predictions)

# Prepare the result DataFrame
last_timestamp = crypto_data['timestamp'].iloc[-1]
next_day = last_timestamp + timedelta(days=1)
current_price = crypto_data['price'].iloc[-1]

result_df = pd.DataFrame({
    'Date': [next_day],
    'Time': [next_day.strftime('%H:%M:%S')],
    'Coin Symbol': [coin_symbols],
    'Current Price': [current_price],
    'Predicted Price': predicted_price.flatten()
})

print(result_df)