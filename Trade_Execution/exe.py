import tkinter as tk
from binance.client import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API Key and Secret from environment variables
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

# Initialize Binance client with testnet environment
client = Client(API_KEY, API_SECRET, testnet=True)

# Set leverage and cost
LEVERAGE = 10
COST = 100

# Set symbol
SYMBOL = 'BTCUSDT'

# Create the GUI window
window = tk.Tk()
window.title("Binance BTC Perp Trading (Testnet)")
window.geometry("400x400")
window.config(bg="#f2f2f2")  # Set background color

# Create a label to display results
result_label = tk.Label(window, text="", font=("Arial", 12), bg="#f2f2f2", fg="#333")
result_label.pack(pady=20)

# Function to update result label
def update_result(message):
    result_label.config(text=message)

# Function to fetch the current BTC price
def get_btc_price():
    ticker = client.futures_symbol_ticker(symbol=SYMBOL)
    return float(ticker['price'])

# Function to calculate the correct quantity of BTC for the trade
def calculate_quantity():
    btc_price = get_btc_price()
    # Position size = COST * LEVERAGE (total exposure)
    position_size = COST * LEVERAGE
    # Quantity of BTC = position size / BTC price
    quantity = position_size / btc_price
    return round(quantity, 3)  # Round to 3 decimal places to match Binance's precision for BTCUSDT

# Function to set leverage
def set_leverage(symbol, leverage):
    try:
        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        return f"Leverage set to {leverage}x for {symbol}"
    except Exception as e:
        return f"Error setting leverage: {e}"

# Function to go long (buy BTC perpetual contract)
def long_btc_perp():
    try:
        # Set leverage
        leverage_message = set_leverage(SYMBOL, LEVERAGE)
        
        # Calculate quantity of BTC to trade
        quantity = calculate_quantity()
        
        # Place a market order to buy BTC perp
        order = client.futures_create_order(
            symbol=SYMBOL,
            side='BUY',
            type='MARKET',
            quantity=quantity,  # Calculated quantity based on leverage and cost
        )
        order_message = f"Long Order Placed: Order ID {order['orderId']}, Status {order['status']}"
        update_result(f"{leverage_message}\n{order_message}")
    except Exception as e:
        update_result(f"Error: {e}")

# Function to go short (sell BTC perpetual contract)
def short_btc_perp():
    try:
        # Set leverage
        leverage_message = set_leverage(SYMBOL, LEVERAGE)
        
        # Calculate quantity of BTC to trade
        quantity = calculate_quantity()
        
        # Place a market order to sell BTC perp
        order = client.futures_create_order(
            symbol=SYMBOL,
            side='SELL',
            type='MARKET',
            quantity=quantity,  # Calculated quantity based on leverage and cost
        )
        order_message = f"Short Order Placed: Order ID {order['orderId']}, Status {order['status']}"
        update_result(f"{leverage_message}\n{order_message}")
    except Exception as e:
        update_result(f"Error: {e}")

# Function to close the current position
def close_position():
    try:
        # Get current position information
        positions = client.futures_position_information(symbol=SYMBOL)
        for position in positions:
            if float(position['positionAmt']) != 0:
                # If position exists, close it
                side = 'SELL' if float(position['positionAmt']) > 0 else 'BUY'
                order = client.futures_create_order(
                    symbol=SYMBOL,
                    side=side,
                    type='MARKET',
                    quantity=abs(float(position['positionAmt']))  # Close the position
                )
                order_message = f"Position Closed: Order ID {order['orderId']}, Status {order['status']}"
                update_result(order_message)
                return
        update_result("No open position to close.")
    except Exception as e:
        update_result(f"Error closing position: {e}")

# Function to check available balance for trading
def check_balance():
    try:
        # Get the available balance in the futures wallet
        account_info = client.futures_account_balance()
        for balance in account_info:
            if balance['asset'] == 'USDT':
                available_balance = balance['balance']
                update_result(f"Available USDT Balance: {available_balance}")
                return
        update_result("USDT balance not found.")
    except Exception as e:
        update_result(f"Error checking balance: {e}")

# Create styled buttons
button_style = {"font": ("Arial", 12), "bg": "#4CAF50", "fg": "white", "activebackground": "#45a049", "width": 20}

long_button = tk.Button(window, text="Long BTC Perp", command=long_btc_perp, **button_style)
long_button.pack(pady=10)

short_button = tk.Button(window, text="Short BTC Perp", command=short_btc_perp, **button_style)
short_button.pack(pady=10)

close_button = tk.Button(window, text="Close Position", command=close_position, **button_style)
close_button.pack(pady=10)

# Add the "Check Balance" button
balance_button = tk.Button(window, text="Check Balance", command=check_balance, **button_style)
balance_button.pack(pady=10)

# Start the GUI main loop
window.mainloop()
