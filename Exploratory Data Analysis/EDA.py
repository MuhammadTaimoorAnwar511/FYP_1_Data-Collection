import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Function to load CSV file
def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        try:
            df = pd.read_csv(file_path)

            # Convert 'Open Time' to datetime
            if 'Open Time' in df.columns:
                df['Open Time'] = pd.to_datetime(df['Open Time'], errors='coerce')
                df = df.dropna(subset=['Open Time'])  # Drop rows with missing 'Open Time'

            messagebox.showinfo("Success", "File loaded successfully!")
            perform_eda(df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
    else:
        messagebox.showwarning("Warning", "No file selected!")

# Function to perform EDA
def perform_eda(df):
    progress['value'] = 10
    root.update_idletasks()

    # Clear previous analysis results from the text box
    analysis_text.delete(1.0, tk.END)

    # Missing values
    analysis_text.insert(tk.END, "Missing values:\n")
    analysis_text.insert(tk.END, str(df.isnull().sum()) + "\n\n")

    progress['value'] = 30
    root.update_idletasks()

    # Correlation matrix (with checkbox for user preference)
    if correlation_var.get() == 1:
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 1:
            plt.figure(figsize=(10, 8))
            sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt='.2f')
            plt.title('Correlation Matrix')
            plt.show()

    progress['value'] = 50
    root.update_idletasks()

    # Histograms
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_cols].hist(bins=20, figsize=(10, 8))
    plt.suptitle('Histograms for Numeric Features')
    plt.show()

    progress['value'] = 70
    root.update_idletasks()

    # Time-series plot (if 'Open Time' exists)
    if 'Open Time' in df.columns and 'Open' in df.columns and 'Close' in df.columns:
        # Drop rows where 'Open' or 'Close' is missing
        df = df.dropna(subset=['Open', 'Close'])
        
        # Set 'Open Time' as the index
        df.set_index('Open Time', inplace=True)
        
        # Check if there's data to plot
        if not df.empty:
            plt.figure(figsize=(10, 6))
            df[['Open', 'Close']].plot()
            plt.title('Open and Close Prices Over Time')
            plt.xlabel('Time')
            plt.ylabel('Price')
            plt.grid(True)  # Adding grid lines for better readability
            plt.legend(title='Price Type')  # Adding legend title
            plt.show()
        else:
            messagebox.showwarning("Warning", "No data available for plotting.")

    progress['value'] = 100
    root.update_idletasks()

# Main GUI
root = tk.Tk()
root.title("Crypto EDA Tool")
root.geometry("600x400")  # Adjusted size
root.config(bg='#f0f0f0')

# Label
label = tk.Label(root, text="Upload a CSV file to perform EDA", font=("Arial", 14), bg='#f0f0f0')
label.pack(pady=10)

# Upload button
upload_button = tk.Button(root, text="Upload CSV", command=load_file, font=("Arial", 12), bg='#4CAF50', fg='white')
upload_button.pack(pady=10)

# Checkbox for correlation matrix
correlation_var = tk.IntVar()
correlation_check = tk.Checkbutton(root, text="Show Correlation Matrix", variable=correlation_var, font=("Arial", 12), bg='#f0f0f0')
correlation_check.pack(pady=5)

# Progress bar
progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
progress.pack(pady=20)

# Text box for displaying analysis results
analysis_text = tk.Text(root, height=15, width=70, font=("Arial", 10))
analysis_text.pack(pady=10)

# Add a scrollbar
scrollbar = tk.Scrollbar(root, command=analysis_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
analysis_text.config(yscrollcommand=scrollbar.set)

root.mainloop()
