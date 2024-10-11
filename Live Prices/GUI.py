import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from matplotlib.animation import FuncAnimation
import time

# Function to read data from the CSV file
def read_data():
    df = pd.read_csv('Live_Candlestick_Data.csv', parse_dates=['Open Time'])
    df.rename(columns={'Open Time': 'timestamp', 'Quote Asset Volume': 'volume_usd', 'Open Interest (USD)': 'open_interest_usd'}, inplace=True)
    return df

# Initialize variables for row counting and plotting
last_row_count = 0
df = pd.DataFrame()

# Create a figure and axes for the plot
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
plt.ion()  # Turn on interactive mode

# Animation function
def update_plot(_):
    global last_row_count, df
    try:
        new_df = read_data()
        current_row_count = new_df.shape[0]  # Get the current number of rows

        # Check if new rows have been added
        if current_row_count > last_row_count:
            print(f"New data detected: {current_row_count - last_row_count} new rows.")
            last_row_count = current_row_count
            df = new_df

            ax1.clear()
            ax2.clear()
            ax3.clear()

            df.set_index('timestamp', inplace=True)

            # Plot candlestick chart
            mpf.plot(df, type='candle', ax=ax1, volume=False, show_nontrading=True)
            ax1.set_title('Price (Candlestick Chart)')

            # Plot volume as bar chart
            ax2.bar(df.index, df['volume_usd'], color='orange', width=0.0005)
            ax2.set_ylabel('Volume (USDT)')
            ax2.set_title('Volume Bar Chart')

            # Plot open interest as line chart
            ax3.plot(df.index, df['open_interest_usd'], color='blue', label='Open Interest (USDT)')
            ax3.set_ylabel('Open Interest (USDT)')
            ax3.set_title('Open Interest Line Chart')
            ax3.legend()

            plt.xticks(rotation=45)
            plt.tight_layout()

    except Exception as e:
        print(f"Error during update: {e}")

# Set up the animation
ani = FuncAnimation(fig, update_plot, interval=5000)  # Update every 5 seconds

# Show the plot
try:
    plt.show(block=True)  # Block execution until the plot window is closed
except Exception as e:
    print(f"An error occurred while showing the plot: {e}")

# Avoid using while True to prevent freezing
while plt.fignum_exists(fig.number):  # Keep the script alive while the figure is open
    time.sleep(1)  # Sleep to prevent CPU overload
