import ccxt
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
    # Calculate the time for the candle that just completed (rounding down to the nearest 5 minutes)
    last_completed_minute = (now - timedelta(minutes=5)).replace(second=0, microsecond=0)
    last_completed_5min = last_completed_minute - timedelta(minutes=last_completed_minute.minute % 5)
    # Convert the timestamp to milliseconds
    since = int(last_completed_5min.timestamp() * 1000)

    try:
        # Add a longer delay (1 seconds) to ensure candle is fully closed and finalized
        time.sleep(1)
        
        # Fetch 5-minute candles starting from the 'since' time
        candles = exchange.fetch_ohlcv(symbol, timeframe='5m', since=since)

        # Return the last completed candle (the most recent one fetched)
        if len(candles) > 0:
            previous_candle = candles[-1]
            if previous_candle[0] == since:  # Ensure it's the exact previous candle
                return {
                    'timestamp': previous_candle[0],
                    'open': previous_candle[1],
                    'high': previous_candle[2],
                    'low': previous_candle[3],
                    'close': previous_candle[4],
                    'volume': previous_candle[5]
                }
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error fetching candle: {e}")
        return None

# Convert timestamp to human-readable format
def format_timestamp(timestamp):
    readable_time = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    return readable_time

# Function to get current UTC time
def get_current_utc_time():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# Example usage to fetch and display the previous candle
while True:
    current_utc_time = get_current_utc_time()  
    
    candle = fetch_previous_candle()
    
    if candle:
        human_readable_timestamp = format_timestamp(candle['timestamp'])
        print(f"Previous Candle: Time: {human_readable_timestamp} - OPEN: {candle['open']} HIGH: {candle['high']} LOW: {candle['low']} CLOSE: {candle['close']} VOLUME: {candle['volume']}")
    else:
        print("Waiting for Current Candle Closing.")

    # Sleep until the start of the next 5-minute interval
    current_time = datetime.now(timezone.utc)
    seconds_to_next_5min = (5 - current_time.minute % 5) * 60 - current_time.second - current_time.microsecond / 1_000_000
    time.sleep(seconds_to_next_5min)
