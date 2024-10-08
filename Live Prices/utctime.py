import datetime
import time
import os

try:
    while True:
        # Get current UTC time
        utc_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        # Clear the console (works for Windows and Unix)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print the UTC time
        print(f'Current UTC Time: {utc_time}')
        
        # Wait for 1 second before updating
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")
