import ccxt
import requests
import time
import csv
from datetime import datetime, timedelta, timezone

# Initialize OKX Futures exchange instance with max precision
exchange = ccxt.okx({
    'options': {
        'defaultType': 'swap',  # Use 'swap' for perpetual contracts in OKX
    },
    'precisionMode': ccxt.TICK_SIZE  # Ensure that price and volume are returned with full precision
})

# CSV file path
csv_file_path = 'Live_Candlestick_Data.csv'

# Write CSV header and clear previous data
def initialize_csv():
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Open Time', 'Open', 'High', 'Low', 'Close', 'Quote Asset Volume', 'Open Interest (USD)'])

# Convert timestamp to human-readable format
def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# Fetch multiple closed candles data
def fetch_recent_candles(symbol='BTC-USDT-SWAP', count=100):
    now = datetime.now(timezone.utc)
    since = int((now - timedelta(minutes=count * 5)).timestamp() * 1000)  # Fetch candles from the past

    try:
        candles = exchange.fetch_ohlcv(symbol, timeframe='5m', since=since, limit=count)
        return candles
    except Exception as e:
        print(f"Error fetching recent candles: {e}")
        return []

# Fetch the previous 5-minute candlestick data for perpetual contract
def fetch_previous_candle(symbol='BTC-USDT-SWAP'):
    now = datetime.now(timezone.utc)
    last_completed_minute = (now - timedelta(minutes=5)).replace(second=0, microsecond=0)
    last_completed_5min = last_completed_minute - timedelta(minutes=last_completed_minute.minute % 5)
    since = int(last_completed_5min.timestamp() * 1000)

    try:
        time.sleep(1)
        candles = exchange.fetch_ohlcv(symbol, timeframe='5m', since=since)

        if len(candles) > 0:
            previous_candle = candles[-1]
            if previous_candle[0] == since:
                volume_usd = previous_candle[4] * previous_candle[5]  # This line can be omitted if you're recalculating below
                return {
                    'timestamp': previous_candle[0],
                    'open': previous_candle[1],
                    'high': previous_candle[2],
                    'low': previous_candle[3],
                    'close': previous_candle[4],
                    'volume_coin': previous_candle[5],
                    'volume_usd': volume_usd
                }
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error fetching candle: {e}")
        return None

# Fetch Open Interest for a specific timestamp
def fetch_open_interest_for_candle(symbol='BTC-USDT-SWAP', candle_timestamp=None):
    if candle_timestamp is None:
        return None

    url = "https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-history"
    start_ts = candle_timestamp
    end_ts = start_ts + 5 * 60 * 1000  # The end of the candle (5 minutes later)

    params = {
        "instId": symbol,
        "period": "5m",
        "begin": str(start_ts),
        "end": str(end_ts),
        "limit": "1"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and data['data']:
            return data['data'][0]
        else:
            print(f"No open interest data found for timestamp {candle_timestamp}")
            return None
    else:
        print(f"Error fetching open interest: {response.status_code} - {response.text}")
        return None

# Function to get current UTC time
def get_current_utc_time():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# Initialize CSV file
initialize_csv()

# Fetch and write the last 100 closed candles
recent_candles = fetch_recent_candles()

if recent_candles:
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        for candle in recent_candles:
            timestamp, open_price, high_price, low_price, close_price, volume = candle
            open_interest_data = fetch_open_interest_for_candle(candle_timestamp=timestamp)
            open_interest_usd = open_interest_data[3] if open_interest_data else 0
            
            # Calculate volume in USD using the closing price
            volume_usd = volume * close_price  # or use another price for better accuracy
            
            writer.writerow([
                format_timestamp(timestamp),
                open_price,
                high_price,
                low_price,
                close_price,
                volume_usd,
                open_interest_usd
            ])
    print(f"Wrote {len(recent_candles)} recent candles to CSV.")

# Continuously fetch data and store in CSV
while True:
    candle = fetch_previous_candle()

    if candle:
        open_interest_data = fetch_open_interest_for_candle(symbol='BTC-USDT-SWAP', candle_timestamp=candle['timestamp'])

        if open_interest_data:
            open_interest_usd = open_interest_data[3]  # Open Interest in USD
            
            # Fetch the latest price for accurate volume calculation
            latest_price = candle['close']  # Or fetch latest price from the exchange for more accuracy

            # Calculate volume in USD using the latest price
            volume_usdt = candle['volume_coin'] * latest_price
            
            # Append the new data to the CSV file
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    format_timestamp(candle['timestamp']),
                    candle['open'],
                    candle['high'],
                    candle['low'],
                    candle['close'],
                    volume_usdt,
                    open_interest_usd
                ])
            print(f"Data written to CSV: Time: {format_timestamp(candle['timestamp'])} - OPEN: {candle['open']} HIGH: {candle['high']} LOW: {candle['low']} CLOSE: {candle['close']} VOLUME (USD): {volume_usdt} OPEN INTEREST (USD): {open_interest_usd}")
        else:
            print("No open interest data available for the candle.")
    else:
        print("Waiting for Current Candle Closing.")

    # Sleep until the start of the next 5-minute interval
    current_time = datetime.now(timezone.utc)
    seconds_to_next_5min = (5 - current_time.minute % 5) * 60 - current_time.second - current_time.microsecond / 1_000_000
    time.sleep(seconds_to_next_5min)
