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

# Mapping from user-friendly names to the actual symbols used by the exchange
symbol_map = {
    'BTC': 'BTC-USDT-SWAP',
    'ETH': 'ETH-USDT-SWAP',
    'SOL': 'SOL-USDT-SWAP',
    'BNB': 'BNB-USDT-SWAP',
    'PEPE': '1000PEPE-USDT-SWAP'
}

# Function to fetch the previous candle based on the selected timeframe
def fetch_previous_candle(symbol, timeframe):
    now = datetime.now(timezone.utc)

    # Calculate the time for the candle that just completed based on the selected timeframe
    if timeframe == '5m':
        last_completed_time = (now - timedelta(minutes=5)).replace(second=0, microsecond=0)
        since = int(last_completed_time.timestamp() * 1000)
        time.sleep(1)
        candles = exchange.fetch_ohlcv(symbol, timeframe='5m', since=since)
    elif timeframe == '1H':
        last_completed_time = (now - timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        since = int(last_completed_time.timestamp() * 1000)
        time.sleep(1)
        candles = exchange.fetch_ohlcv(symbol, timeframe='1h', since=since)
    elif timeframe == '4H':
        last_completed_time = (now - timedelta(hours=4)).replace(minute=0, second=0, microsecond=0)
        since = int(last_completed_time.timestamp() * 1000)
        time.sleep(1)
        candles = exchange.fetch_ohlcv(symbol, timeframe='4h', since=since)
    elif timeframe == '1D':
        last_completed_time = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        since = int(last_completed_time.timestamp() * 1000)
        time.sleep(1)
        candles = exchange.fetch_ohlcv(symbol, timeframe='1d', since=since)
    else:
        print("Invalid timeframe selected.")
        return None

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
    return None

# Fetch Open Interest for a specific timestamp
def fetch_open_interest_for_candle(symbol, candle_timestamp):
    if candle_timestamp is None:
        return None

    url = "https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-history"
    
    # Use the candle's timestamp to fetch Open Interest for that specific timeframe
    start_ts = candle_timestamp
    if timeframe == '5m':
        end_ts = start_ts + 5 * 60 * 1000  # 5 minutes later
    elif timeframe == '1H':
        end_ts = start_ts + 60 * 60 * 1000  # 1 hour later
    elif timeframe == '4H':
        end_ts = start_ts + 4 * 60 * 60 * 1000  # 4 hours later
    elif timeframe == '1D':
        end_ts = start_ts + 24 * 60 * 60 * 1000  # 1 day later
    else:
        return None

    params = {
        "instId": symbol,
        "period": timeframe.upper(),  # Ensure we're using a compatible period
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

# Main execution
if __name__ == "__main__":
    # User input for timeframe and coin selection
    timeframe = input("Select timeframe (5m, 1H, 4H, 1D): ").strip()
    coin = input("Select coin (BTC, ETH, SOL, BNB, PEPE): ").strip().upper()

    if coin in symbol_map:
        symbol = symbol_map[coin]
    else:
        print("Invalid coin selected. Exiting.")
        exit()

    # Example usage to fetch and display the previous candle along with open interest
    while True:
        candle = fetch_previous_candle(symbol, timeframe)

        if candle:
            open_interest_data = fetch_open_interest_for_candle(symbol, candle['timestamp'])

            if open_interest_data:
                human_readable_timestamp = format_timestamp(candle['timestamp'])
                open_interest_usd = open_interest_data[3]  # Open Interest in USD
                print(f"Previous Candle: Time: {human_readable_timestamp} - OPEN: {candle['open']} HIGH: {candle['high']} LOW: {candle['low']} CLOSE: {candle['close']} VOLUME (USD): {candle['volume_usd']} OPEN INTEREST (USD): {open_interest_usd}")
            else:
                print("No open interest data available for the candle.")

        else:
            print("Waiting for Current Candle Closing.")

        # Sleep until the next candle based on the selected timeframe
        if timeframe == '5m':
            time.sleep(300)  # Sleep for 5 minutes
        elif timeframe == '1H':
            time.sleep(3600)  # Sleep for 1 hour
        elif timeframe == '4H':
            time.sleep(14400)  # Sleep for 4 hours
        elif timeframe == '1D':
            time.sleep(86400)  # Sleep for 1 day
