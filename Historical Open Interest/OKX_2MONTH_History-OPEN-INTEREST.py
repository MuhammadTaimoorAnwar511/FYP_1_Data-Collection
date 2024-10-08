import requests
import csv
from datetime import datetime, timedelta, timezone

def unix_to_human(timestamp):
    """Convert Unix timestamp to human-readable format with timezone-aware UTC."""
    return datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# Define the API endpoint
url = "https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-history"

# Initialize request counter
request_counter = 0

# Calculate the current UTC time and 1440 hours ago (60 days)
end_date = datetime.now(tz=timezone.utc).replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
start_date = end_date - timedelta(hours=1440)

# Symbols and intervals to loop through
#symbols = ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "BNB-USDT-SWAP", "SOL-USDT-SWAP", "1000PEPE-USDT-SWAP"]
#intervals = ["1H", "4H", "1D"]  # Adjusted intervals according to the valid periods
symbols = ["BTC-USDT-SWAP"]
intervals = ["1H"]  # Adjusted intervals according to the valid periods

print(f"Fetching data for {symbols} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")

for symbol in symbols:
    for interval in intervals:
        all_data = []
        symbol_name = symbol.replace('USDT-SWAP', '')
        current_date = start_date

        while current_date <= end_date:
            start_ts = int(current_date.timestamp() * 1000)
            end_ts = int((current_date + timedelta(hours=24)).timestamp() * 1000)

            print(f"Fetching {interval} data for {symbol} on {current_date.strftime('%Y-%m-%d')}...")

            params = {
                "instId": symbol,
                "period": interval,
                "begin": str(start_ts),
                "end": str(end_ts),
                "limit": "24"
            }

            response = requests.get(url, params=params)
            request_counter += 1

            data = response.json()
           # print(f"Response Data for {symbol} on {current_date.strftime('%Y-%m-%d')}: {data}")

            if response.status_code == 200:
                if 'data' in data:
                    if data['data']:
                        all_data.extend(data['data'])
                    else:
                        print(f"No data found for {current_date.strftime('%Y-%m-%d')} for {symbol}")
                else:
                    print(f"Unexpected response structure for {symbol}")
            else:
                print(f"Error: {response.status_code} - {response.text} for {symbol}")

            current_date += timedelta(hours=24)

        if all_data:
            all_data.sort(key=lambda x: x[0])
            file_name = f"{symbol_name}_{interval}_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv"
            
            with open(file_name, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Time', 'Open Interest (Contracts)', 'Open Interest (Crypto)', 'Open Interest (USD)'])
                
                for record in all_data:
                    timestamp, oi, oiCcy, oiUsd = record
                    human_time = unix_to_human(timestamp)
                    writer.writerow([human_time, oi, oiCcy, oiUsd])

            print(f"Data for {symbol} ({interval}) has been written to {file_name}")
        else:
            print(f"No data to write for {symbol} ({interval})")

print(f"Number of requests sent: {request_counter}")
