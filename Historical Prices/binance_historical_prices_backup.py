import requests
from requests.exceptions import ConnectionError
import pandas as pd
from datetime import datetime, timedelta
import time

def fetch_binance_futures_data(symbol, interval, start_time, end_time):
    base_url = "https://fapi.binance.com"
    endpoint = "/fapi/v1/klines"
    
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": int(start_time.timestamp() * 1000),
        "endTime": int(end_time.timestamp() * 1000),
        "limit": 1000
    }
    
    retries = 5
    for attempt in range(retries):
        try:
            response = requests.get(base_url + endpoint, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except ConnectionError as e:
            print(f"Connection error: {e}. Retrying in {2 ** attempt} seconds...")
            time.sleep(2 ** attempt)  # Exponential backoff
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {symbol} at {interval}: {e}")
            return None
    print(f"Failed to fetch data for {symbol} after {retries} attempts.")
    return None

def save_data_to_csv(data, symbol, interval, start_date, end_date):
    # Convert data to DataFrame and select only required columns
    df = pd.DataFrame(data, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])
    
    # Keep only the specified columns
    df = df[["Open Time", "Open", "High", "Low", "Close", "Volume"]]
    
    # Convert timestamps to human-readable dates
    df["Open Time"] = pd.to_datetime(df["Open Time"], unit='ms')
    
    # Sort the data by the "Open Time" column
    df.sort_values(by="Open Time", inplace=True)
    
    # Format the CSV file name
    symbol_name = symbol.replace('USDT', '')  # Clean the symbol name
    file_name = f"{symbol_name}_{interval}_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv"
    
    # Save to CSV
    df.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}")
    print("----------------------------\n")

def main():
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "1000PEPEUSDT"]  # List of symbols
    intervals = ["1h", "4h", "1d"]  # Intervals: 1-hour, 4-hour, 1-day
    default_start_date = datetime.strptime("2024-09-01", "%Y-%m-%d")  # Default start date
    end_date = datetime.strptime("2024-09-03", "%Y-%m-%d")    # End date (exclusive)
    
    for symbol in symbols:
        # Set the specific start date for 1000PEPEUSDT
        if symbol == "1000PEPEUSDT":
            start_date = datetime.strptime("2023-05-05", "%Y-%m-%d")
        else:
            start_date = default_start_date
        
        for interval in intervals:
            current_date = start_date
            all_data = []
            
            while current_date < end_date:
                next_date = current_date + timedelta(days=1)
                
                print(f"Fetching {interval} data for {symbol} on {current_date.strftime('%Y-%m-%d')}")
                
                # Fetch data for the current day
                data = fetch_binance_futures_data(symbol, interval, current_date, next_date)
                
                if data:
                    all_data.extend(data)
                
                current_date = next_date
                time.sleep(1)  # Add a 1-second delay after each request
            
            if all_data:
                save_data_to_csv(all_data, symbol, interval, start_date, end_date)

if __name__ == "__main__":
    main()
