import ccxt
import requests
import time
from datetime import datetime, timedelta, timezone

# Initialize OKX Futures exchange instance with max precision
exchange = ccxt.okx({
    'options': {
        'defaultType': 'swap',  # Use 'swap' for perpetual contracts in OKX
    },
    'precisionMode': ccxt.TICK_SIZE  # Ensure that price and volume are returned with full precision
})

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
                volume_usd = previous_candle[4] * previous_candle[5]
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

    # Use the candle's timestamp to fetch Open Interest for that specific timeframe
    start_ts = candle_timestamp  # The start of the candle
    end_ts = start_ts + 5 * 60 * 1000  # The end of the candle (5 minutes later)

    params = {
        "instId": symbol,
        "period": "5m",  # Ensure we're using a compatible period
        "begin": str(start_ts),
        "end": str(end_ts),
        "limit": "1"  # Fetch only one data point for the specific period
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and data['data']:
            return data['data'][0]  # Return the first entry that matches the timestamp
        else:
            print(f"No open interest data found for timestamp {candle_timestamp}")
            return None
    else:
        print(f"Error fetching open interest: {response.status_code} - {response.text}")
        return None

# Convert timestamp to human-readable format
def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# Function to get current UTC time
def get_current_utc_time():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# Example usage to fetch and display the previous candle along with open interest
while True:
    current_utc_time = get_current_utc_time()  
    
    candle = fetch_previous_candle()
    
    if candle:
        open_interest_data = fetch_open_interest_for_candle(symbol='BTC-USDT-SWAP', candle_timestamp=candle['timestamp'])

        if open_interest_data:
            human_readable_timestamp = format_timestamp(candle['timestamp'])
            # Open interest data can be unpacked accordingly
            open_interest_contracts = open_interest_data[1]  # Open Interest in Contracts
            open_interest_usd = open_interest_data[3]  # Open Interest in USD
            # print(f"Previous Candle: Time: {human_readable_timestamp} - OPEN: {candle['open']} HIGH: {candle['high']} LOW: {candle['low']} CLOSE: {candle['close']} VOLUME (Coins): {candle['volume_coin']} VOLUME (USD): {candle['volume_usd']} OPEN INTEREST (Contracts): {open_interest_contracts} OPEN INTEREST (USD): {open_interest_usd}")
            print(f"Previous Candle: Time: {human_readable_timestamp} - OPEN: {candle['open']} HIGH: {candle['high']} LOW: {candle['low']} CLOSE: {candle['close']} VOLUME (USD): {candle['volume_usd']} OPEN INTEREST (USD): {open_interest_usd}")
        else:
            print("No open interest data available for the candle.")

    else:
        print("Waiting for Current Candle Closing.")

    # Sleep until the start of the next 5-minute interval
    current_time = datetime.now(timezone.utc)
    seconds_to_next_5min = (5 - current_time.minute % 5) * 60 - current_time.second - current_time.microsecond / 1_000_000
    time.sleep(seconds_to_next_5min)
