import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Text
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



# Initialize global variable to store the DataFrame
data = None

class CSVUploaderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CSV Uploader")
        self.master.geometry("600x500")
        self.master.config(bg="#2E2E2E") 
        self.df = None
        self.create_upload_frame()

    def create_upload_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        self.upload_button = tk.Button(self.master, text="Upload CSV", command=self.upload_csv, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
        self.upload_button.pack(pady=20)

        self.status_label = tk.Label(self.master, text="", font=("Arial", 12), bg="#2E2E2E", fg="white")
        self.status_label.pack(pady=10)

    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                # Read CSV file
                self.df = pd.read_csv(file_path)
                # Convert 'Open Time' to datetime for time-based analysis
                self.df['Open Time'] = pd.to_datetime(self.df['Open Time'], errors='coerce')
                self.status_label.config(text=f"CSV file uploaded successfully: {file_path}")
                self.create_menu_frame()
                self.analyze_data()  # Perform analysis after switching frames
            except Exception as e:
                self.status_label.config(text=f"Error uploading file: {str(e)}")

    def create_menu_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        menu_frame = tk.Frame(self.master, bg="#2E2E2E")
        menu_frame.pack(fill=tk.BOTH, expand=True)

        menu_label = tk.Label(menu_frame, text="Menu", font=("Arial", 16), bg="#2E2E2E", fg="white")
        menu_label.pack(pady=20)

        back_button = tk.Button(menu_frame, text="Back to Upload CSV", command=self.create_upload_frame, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
        back_button.pack(pady=10)

        stats_button = tk.Button(menu_frame, text="Basic Descriptive Statistics", command=self.show_statistics, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
        stats_button.pack(pady=10)

        plot_button = tk.Button(menu_frame, text="Time Series Plots", command=self.plot_time_series, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
        plot_button.pack(pady=10)

        price_analysis_button = tk.Button(menu_frame, text="Price Analysis", command=self.price_analysis, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
        price_analysis_button.pack(pady=10)

        volume_analysis_button = tk.Button(menu_frame, text="Volume Analysis", command=self.volume_analysis, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
        volume_analysis_button.pack(pady=10)

        # Add Open Interest Analysis Button
        open_interest_button = tk.Button(menu_frame, text="Open Interest Analysis", command=self.open_interest_analysis, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
        open_interest_button.pack(pady=10)

        # Add Correlation Analysis Button
        correlation_analysis_button = tk.Button(menu_frame, text="Correlation Analysis", command=self.correlation_analysis, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
        correlation_analysis_button.pack(pady=10)

        # Add Outlier Detection Button
        outlier_detection_button = tk.Button(menu_frame, text="Outlier Detection", command=self.outlier_detection_analysis, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
        outlier_detection_button.pack(pady=10)

    def analyze_data(self):
        # Basic Descriptive Statistics
        num_rows = len(self.df)
        missing_values = self.df.isnull().sum().sum()  # Total missing values in the dataset
        unique_rows = len(self.df.drop_duplicates())
        duplicate_rows = num_rows - unique_rows  # Number of duplicate rows
        negative_values = (self.df.select_dtypes(include=['number']) < 0).sum().sum()  # Count of negative values in numeric columns

        # Detect missing dates or time gaps in 'Open Time' for daily/interval-based data
        data_sorted = self.df.sort_values(by='Open Time')  # Sort by 'Open Time'
        
        # Calculate the difference between consecutive dates
        date_diff = data_sorted['Open Time'].diff().dt.days  # Assuming daily data here
        missing_dates = (date_diff > 1).sum()  # Number of missing date gaps
        
        # Check if 'Open Time' is in ascending order
        is_ascending = self.df['Open Time'].is_monotonic_increasing

        # Check for duplicate timestamps
        duplicate_timestamps = self.df['Open Time'].duplicated().sum()  # Count of duplicate timestamps
        unique_timestamps = len(self.df['Open Time']) - duplicate_timestamps  # Unique timestamps

        # Identify rows with issues
        missing_rows = self.df[self.df.isnull().any(axis=1)].index.tolist()  # Row indices with missing values
        duplicate_row_indices = self.df[self.df.duplicated(keep=False)].index.tolist()  # All duplicate row indices
        negative_row_indices = self.df[(self.df.select_dtypes(include=['number']) < 0).any(axis=1)].index.tolist()  # Rows with negative values

        # Adjust row indices for display (add 1)
        missing_rows_display = [i + 2 for i in missing_rows]
        duplicate_row_indices_display = [i + 2 for i in duplicate_row_indices]
        negative_row_indices_display = [i + 2 for i in negative_row_indices]

        # Store results for display
        self.stats_text = (
            f"Total Rows: {num_rows}\n"
            f"Missing Values (total): {missing_values}\n"
            f"Unique Rows: {unique_rows}\n"
            f"Duplicate Rows: {duplicate_rows}\n"
            f"Negative Values (numeric columns): {negative_values}\n"
            f"Missing Date Gaps: {missing_dates} (gaps in 'Open Time')\n"
            f"Is 'Open Time' in Ascending Order: {'Yes' if is_ascending else 'No'}\n"
            f"Duplicate Timestamps: {duplicate_timestamps} (out of {num_rows})\n"
            f"Unique Timestamps: {unique_timestamps}\n"
        )
        # Row numbers causing issues
        self.issues_text = (
            f"Row Numbers with Missing Values: {missing_rows_display}\n"
            f"Row Numbers with Duplicate Entries: {duplicate_row_indices_display}\n"
            f"Row Numbers with Negative Values: {negative_row_indices_display}\n"
        )

    def show_statistics(self):
        if self.df is not None:
            self.create_statistics_frame()
        else:
            messagebox.showerror("Error", "No CSV file has been uploaded yet.")

    def create_statistics_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        stats_frame = tk.Frame(self.master, bg="#2E2E2E")
        stats_frame.pack(fill=tk.BOTH, expand=True)

        stats_label = tk.Label(stats_frame, text="Basic Descriptive Statistics", font=("Arial", 16), bg="#2E2E2E", fg="white")
        stats_label.pack(pady=20)

        # Create a Text widget with a scrollbar
        scroll_bar = Scrollbar(stats_frame)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        stats_output = Text(stats_frame, wrap=tk.WORD, yscrollcommand=scroll_bar.set, width=80, height=40, bg="#FFFFFF")
        stats_output.pack(pady=10, padx=10)

        scroll_bar.config(command=stats_output.yview)

        # Insert statistics and issues into Text widget
        stats_output.insert(tk.END, self.stats_text + "\n" + "Issues Identified:\n" + self.issues_text)

        back_button = tk.Button(stats_frame, text="Back to Menu", command=self.create_menu_frame, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
        back_button.pack(pady=10)

    def plot_time_series(self):
            if self.df is not None:
                self.create_plot_frame()
            else:
                messagebox.showerror("Error", "No CSV file has been uploaded yet.")

    def create_plot_frame(self):
        try:
            # Clear existing widgets
            for widget in self.master.winfo_children():
                widget.destroy()

            plot_frame = tk.Frame(self.master, bg="#2E2E2E")
            plot_frame.pack(fill=tk.BOTH, expand=True)

            plot_label = tk.Label(plot_frame, text="Time Series Plots", font=("Arial", 16), bg="#2E2E2E", fg="white")
            plot_label.pack(pady=20)

            # Set index and prepare columns for plotting
            self.df.set_index('Open Time', inplace=True)
            
            # Check if the necessary columns exist
            if 'Open' in self.df.columns and 'Close' in self.df.columns and 'Quote Asset Volume' in self.df.columns:
                # Create a figure with subplots
                fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

                # Plot Opening and Closing prices
                axs[0].plot(self.df.index, self.df['Open'], label='Open', color='green', linewidth=1.5)
                axs[0].plot(self.df.index, self.df['Close'], label='Close', color='red', linewidth=1.5)
                axs[0].set_title('Opening and Closing Prices')
                axs[0].set_ylabel('Price')
                axs[0].legend()

                # Plot Quote Asset Volume as a bar chart
                axs[1].bar(self.df.index, self.df['Quote Asset Volume'], color='blue', alpha=0.6)
                axs[1].set_title('Quote Asset Volume Histogram')
                axs[1].set_ylabel('Quote Asset Volume')

                # Optional: You could add a third plot for Open Interest if needed
                if 'Open Interest (USD)' in self.df.columns:
                    axs[2].plot(self.df.index, self.df['Open Interest (USD)'], label='Open Interest', color='purple', linewidth=1.5)
                    axs[2].set_title('Open Interest Over Time')
                    axs[2].set_ylabel('Open Interest')
                    axs[2].legend()

                plt.xlabel('Time')
                plt.tight_layout()
                plt.show()
            else:
                messagebox.showerror("Error", "Required columns (Open, Close, Quote Asset Volume) are missing from the data.")

            back_button = tk.Button(plot_frame, text="Back to Menu", command=self.create_menu_frame, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
            back_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the plot frame: {str(e)}")

    def price_analysis(self):
        if self.df is not None:
            try:
                # Clear existing widgets
                for widget in self.master.winfo_children():
                    widget.destroy()

                analysis_frame = tk.Frame(self.master, bg="#2E2E2E")
                analysis_frame.pack(fill=tk.BOTH, expand=True)

                analysis_label = tk.Label(analysis_frame, text="Price Analysis", font=("Arial", 16), bg="#2E2E2E", fg="white")
                analysis_label.pack(pady=20)

                # Scatter plot: Open vs Close
                plt.figure(figsize=(12, 6))
                plt.subplot(1, 2, 1)
                plt.scatter(self.df['Open'], self.df['Close'], color='blue', alpha=0.5)
                plt.title('Open vs Close Price')
                plt.xlabel('Open Price')
                plt.ylabel('Close Price')

                # Scatter plot: High vs Low
                plt.subplot(1, 2, 2)
                plt.scatter(self.df['High'], self.df['Low'], color='green', alpha=0.5)
                plt.title('High vs Low Price')
                plt.xlabel('High Price')
                plt.ylabel('Low Price')

                plt.tight_layout()
                plt.show()

                # Calculating volatility (High-Low spread)
                self.df['Volatility'] = self.df['High'] - self.df['Low']

                # Moving averages
                self.df['MA200'] = self.df['Close'].rolling(window=200).mean()

                # Plot closing price with moving averages
                plt.figure(figsize=(10, 6))
                plt.plot(self.df['Close'], label='Close Price', color='blue')
                plt.plot(self.df['MA200'], label='200-Day Moving Average', color='orange')
                plt.title('Closing Price and 200-Day Moving Average')
                plt.xlabel('Time')
                plt.ylabel('Price')
                plt.legend()
                plt.show()

                back_button = tk.Button(analysis_frame, text="Back to Menu", command=self.create_menu_frame, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
                back_button.pack(pady=10)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during price analysis: {str(e)}")
        else:
            messagebox.showerror("Error", "No CSV file has been uploaded yet.")

    def volume_analysis(self):
        if self.df is not None:
            try:
                # Clear existing widgets
                for widget in self.master.winfo_children():
                    widget.destroy()

                analysis_frame = tk.Frame(self.master, bg="#2E2E2E")
                analysis_frame.pack(fill=tk.BOTH, expand=True)

                analysis_label = tk.Label(analysis_frame, text="Volume Analysis", font=("Arial", 16), bg="#2E2E2E", fg="white")
                analysis_label.pack(pady=20)

                # Create figure for scatter plots: Trading Volume vs Close Price and Quote Asset Volume vs Close Price
                fig, axs = plt.subplots(1, 2, figsize=(14, 6))
                
                # Scatter plot: Volume vs Close Price
                axs[0].scatter(self.df['Volume'], self.df['Close'], color='blue', alpha=0.5)
                axs[0].set_title('Trading Volume vs Close Price')
                axs[0].set_xlabel('Volume')
                axs[0].set_ylabel('Close Price')

                # Scatter plot: Quote Asset Volume vs Close Price
                if 'Quote Asset Volume' in self.df.columns:
                    axs[1].scatter(self.df['Quote Asset Volume'], self.df['Close'], color='green', alpha=0.5)
                    axs[1].set_title('Quote Asset Volume vs Close Price')
                    axs[1].set_xlabel('Quote Asset Volume')
                    axs[1].set_ylabel('Close Price')

                plt.tight_layout()
                plt.show()

                # Create figure for time series plots: Volume over time and Quote Asset Volume over time
                fig, axs = plt.subplots(2, 1, figsize=(12, 10))

                # Plot Volume over time
                axs[0].plot(self.df.index, self.df['Volume'], label='Volume', color='blue')
                axs[0].set_title('Volume Over Time')
                axs[0].set_xlabel('Time')
                axs[0].set_ylabel('Volume')

                # Plot Quote Asset Volume over time
                if 'Quote Asset Volume' in self.df.columns:
                    axs[1].plot(self.df.index, self.df['Quote Asset Volume'], label='Quote Asset Volume', color='orange')
                    axs[1].set_title('Quote Asset Volume Over Time')
                    axs[1].set_xlabel('Time')
                    axs[1].set_ylabel('Quote Asset Volume')

                plt.tight_layout()
                plt.show()

                back_button = tk.Button(analysis_frame, text="Back to Menu", command=self.create_menu_frame, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
                back_button.pack(pady=10)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during volume analysis: {str(e)}")
        else:
            messagebox.showerror("Error", "No CSV file has been uploaded yet.")
   
    def open_interest_analysis(self):
        if self.df is not None:
            try:
                # Clear existing widgets
                for widget in self.master.winfo_children():
                    widget.destroy()

                # Create a figure for the first plot: Open Interest vs Close Price
                if 'Open Interest (USD)' in self.df.columns and 'Close' in self.df.columns:
                    plt.figure(figsize=(8, 6))
                    plt.scatter(self.df['Open Interest (USD)'], self.df['Close'], color='purple', alpha=0.5)
                    plt.title('Open Interest vs Close Price')
                    plt.xlabel('Open Interest (USD)')
                    plt.ylabel('Close Price')
                    plt.tight_layout()
                    plt.show()
                    plt.close()  # Close the figure after showing it

                # Create a figure with two subplots for the next two plots
                fig, axs = plt.subplots(1, 2, figsize=(16, 6))

                # Scatter plot: Open Interest vs Trading Volume (Left)
                if 'Open Interest (USD)' in self.df.columns and 'Volume' in self.df.columns:
                    axs[0].scatter(self.df['Open Interest (USD)'], self.df['Volume'], color='blue', alpha=0.5)
                    axs[0].set_title('Open Interest vs Trading Volume')
                    axs[0].set_xlabel('Open Interest (USD)')
                    axs[0].set_ylabel('Trading Volume')

                # Scatter plot: Open Interest vs Quote Asset Volume (Right)
                if 'Open Interest (USD)' in self.df.columns and 'Quote Asset Volume' in self.df.columns:
                    axs[1].scatter(self.df['Open Interest (USD)'], self.df['Quote Asset Volume'], color='green', alpha=0.5)
                    axs[1].set_title('Open Interest vs Quote Asset Volume')
                    axs[1].set_xlabel('Open Interest (USD)')
                    axs[1].set_ylabel('Quote Asset Volume')

                plt.tight_layout()
                plt.show()

                # Back button
                back_button = tk.Button(self.master, text="Back to Menu", command=self.create_menu_frame, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
                back_button.pack(pady=10)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during Open Interest analysis: {str(e)}")
        else:
            messagebox.showerror("Error", "No CSV file has been uploaded yet.")

    def correlation_analysis(self):
        if self.df is not None:
            try:
                # Clear existing widgets
                for widget in self.master.winfo_children():
                    widget.destroy()

                # Define the columns to consider for correlation
                columns_to_consider = ['Close', 'Volume', 'Quote Asset Volume']

                # Check if 'Open Interest (USD)' is in the dataframe
                if 'Open Interest (USD)' in self.df.columns:
                    columns_to_consider.append('Open Interest (USD)')

                # Create a subset of the DataFrame with only the relevant columns
                relevant_df = self.df[columns_to_consider].dropna()

                # Calculate the correlation matrix
                correlation_matrix = relevant_df.corr()

                # Create a heatmap for the correlation matrix
                plt.figure(figsize=(10, 8))
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
                plt.title('Correlation Matrix')
                plt.tight_layout()
                plt.show()

                # Back button
                back_button = tk.Button(self.master, text="Back to Menu", command=self.create_menu_frame, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
                back_button.pack(pady=10)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during Correlation Analysis: {str(e)}")
        else:
            messagebox.showerror("Error", "No CSV file has been uploaded yet.")

    def outlier_detection_analysis(self):
        if self.df is not None:
            try:
                # Clear existing widgets
                for widget in self.master.winfo_children():
                    widget.destroy()

                # Define the columns for analysis
                columns_to_analyze = ['Close', 'Volume', 'Quote Asset Volume', 'Open Interest (USD)']

                # Check if these columns are in the dataframe
                for col in columns_to_analyze:
                    if col in self.df.columns:
                        # Calculate the Z-scores
                        self.df[f'{col} Z-Score'] = (self.df[col] - self.df[col].mean()) / self.df[col].std()

                # Create a new figure for the outlier detection results
                plt.figure(figsize=(12, 8))
                for i, col in enumerate(columns_to_analyze):
                    if col in self.df.columns:
                        plt.subplot(2, 2, i + 1)
                        plt.scatter(self.df.index, self.df[col], color='blue', alpha=0.5)
                        plt.axhline(y=self.df[col].mean() + 3 * self.df[col].std(), color='red', linestyle='--', label='Upper Outlier Threshold')
                        plt.axhline(y=self.df[col].mean() - 3 * self.df[col].std(), color='red', linestyle='--', label='Lower Outlier Threshold')
                        plt.title(f'Outlier Detection for {col}')
                        plt.xlabel('Index')
                        plt.ylabel(col)
                        plt.legend()

                plt.tight_layout()
                plt.show()

                # Back button
                back_button = tk.Button(self.master, text="Back to Menu", command=self.create_menu_frame, font=("Arial", 12), bg="#3498DB", fg="white", padx=10, pady=5)
                back_button.pack(pady=10)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during Outlier Detection: {str(e)}")
        else:
            messagebox.showerror("Error", "No CSV file has been uploaded yet.")




if __name__ == "__main__":
    root = tk.Tk()
    app = CSVUploaderApp(root)
    root.mainloop()
