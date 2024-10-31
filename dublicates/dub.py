import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from pandas.tseries.frequencies import to_offset

class DataAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Analyzer")
        self.df = None  # DataFrame to hold the CSV data
        self.file_name = ""  # Variable to store the uploaded file name

        # Initialize frames
        self.init_upload_frame()
        self.init_result_frame()

    def init_upload_frame(self):
        self.upload_frame = tk.Frame(self.root)
        self.upload_frame.pack(fill="both", expand=True)

        title = tk.Label(self.upload_frame, text="Upload CSV File", font=("Arial", 16))
        title.pack(pady=10)

        upload_button = tk.Button(self.upload_frame, text="Choose File", command=self.upload_file)
        upload_button.pack(pady=10)

    def init_result_frame(self):
        self.result_frame = tk.Frame(self.root)

        # Text areas to display stats and issues
        self.stats_text_widget = tk.Text(self.result_frame, height=12, width=80)
        self.issues_text_widget = tk.Text(self.result_frame, height=12, width=80)

        # Add scrollbars to text widgets
        self.stats_scroll = tk.Scrollbar(self.result_frame, command=self.stats_text_widget.yview)
        self.issues_scroll = tk.Scrollbar(self.result_frame, command=self.issues_text_widget.yview)
        self.stats_text_widget.config(yscrollcommand=self.stats_scroll.set)
        self.issues_text_widget.config(yscrollcommand=self.issues_scroll.set)

        # Place widgets on result frame
        self.stats_text_widget.grid(row=0, column=0, padx=10, pady=5)
        self.stats_scroll.grid(row=0, column=1, sticky='ns')
        self.issues_text_widget.grid(row=1, column=0, padx=10, pady=5)
        self.issues_scroll.grid(row=1, column=1, sticky='ns')

        # Remove duplicates button
        remove_duplicates_button = tk.Button(self.result_frame, text="Remove Duplicates", command=self.remove_duplicates)
        remove_duplicates_button.grid(row=2, column=0, pady=10)

        # Back button
        back_button = tk.Button(self.result_frame, text="Back", command=self.back_to_upload)
        back_button.grid(row=3, column=0, pady=10)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_name = file_path.split("/")[-1]  # Extract the file name from the path
            try:
                self.df = pd.read_csv(file_path, parse_dates=['Open Time'])
                self.analyze_data()
                self.show_result_frame()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def analyze_data(self):
        # Basic Descriptive Statistics
        num_rows = len(self.df)
        missing_values = self.df.isnull().sum().sum()
        unique_rows = len(self.df.drop_duplicates())
        duplicate_rows = num_rows - unique_rows
        negative_values = (self.df.select_dtypes(include=['number']) < 0).sum().sum()

        # Sort data by 'Open Time' and detect missing time intervals
        data_sorted = self.df.sort_values(by='Open Time').reset_index(drop=True)

        # Determine the expected time frequency
        time_diffs = data_sorted['Open Time'].diff().dropna()  # Calculate time differences between consecutive timestamps
        min_time_diff = time_diffs.min() if not time_diffs.empty else pd.Timedelta(0)  # Avoid empty min error

        # Detect the closest standard frequency
        if min_time_diff <= pd.Timedelta(hours=1):
            expected_freq = '1H'
        elif min_time_diff <= pd.Timedelta(hours=4):
            expected_freq = '4H'
        elif min_time_diff <= pd.Timedelta(days=1):
            expected_freq = '1D'
        else:
            expected_freq = min_time_diff  # Fallback if an unsupported interval is detected

        # Calculate gaps based on the detected frequency
        expected_timedelta = pd.Timedelta(to_offset(expected_freq).nanos, unit='ns')

        # Ensure `time_diffs` and its length matches the DataFrame
        missing_dates = (time_diffs > expected_timedelta).sum()
        is_ascending = data_sorted['Open Time'].is_monotonic_increasing
        duplicate_timestamps = self.df['Open Time'].duplicated().sum()
        unique_timestamps = num_rows - duplicate_timestamps

        # Identify the row indices where the gaps occur
        gap_indices = time_diffs.index[time_diffs > expected_timedelta].tolist()  # Index of time_diffs directly
        gap_indices_display = [i + 2 for i in gap_indices]  # Adjust for 0-based indexing

        # Identify rows with issues
        missing_rows = self.df[self.df.isnull().any(axis=1)].index.tolist()
        duplicate_row_indices = self.df[self.df.duplicated(keep=False)].index.tolist()
        negative_row_indices = self.df[(self.df.select_dtypes(include=['number']) < 0).any(axis=1)].index.tolist()

        missing_rows_display = [i + 2 for i in missing_rows]  # Adjust for 0-based indexing
        duplicate_row_indices_display = [i + 2 for i in duplicate_row_indices]
        negative_row_indices_display = [i + 2 for i in negative_row_indices]

        # Store results for display
        self.stats_text = (
            f"File Name: {self.file_name}\n"
            f"Total Rows: {num_rows}\n"
            f"Missing Values (total): {missing_values}\n"
            f"Unique Rows: {unique_rows}\n"
            f"Duplicate Rows: {duplicate_rows}\n"
            f"Negative Values (numeric columns): {negative_values}\n"
            f"Expected Interval: {expected_freq}\n"
            f"Missing Date Gaps: {missing_dates} (gaps in 'Open Time')\n"
            f"Is 'Open Time' in Ascending Order: {'Yes' if is_ascending else 'No'}\n"
            f"Duplicate Timestamps: {duplicate_timestamps} (out of {num_rows})\n"
            f"Unique Timestamps: {unique_timestamps}\n"
        )
        self.issues_text = (
            f"Row Numbers with Missing Values: {missing_rows_display}\n"
            f"Row Numbers with Duplicate Entries: {duplicate_row_indices_display}\n"
            f"Row Numbers with Negative Values: {negative_row_indices_display}\n"
            f"Rows with Missing Date Gaps: {gap_indices_display}\n"
        )    
    def remove_duplicates(self):
        # Only keep the first occurrence of each duplicate, remove subsequent duplicates
        initial_rows = len(self.df)
        self.df = self.df[self.df.duplicated(keep='first') == False]
        final_rows = len(self.df)
        duplicates_removed = initial_rows - final_rows

        # Save the updated DataFrame back to the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.df.to_csv(file_path, index=False)
            messagebox.showinfo("Info", f"Removed {duplicates_removed} duplicate rows and saved to {file_path}.")

        # Update analysis after removing duplicates
        self.analyze_data()

        # Update display
        self.stats_text_widget.delete(1.0, tk.END)
        self.issues_text_widget.delete(1.0, tk.END)
        self.stats_text_widget.insert(tk.END, self.stats_text)
        self.issues_text_widget.insert(tk.END, self.issues_text) 

    def show_result_frame(self):
        # Update text widgets with results
        self.stats_text_widget.delete(1.0, tk.END)
        self.issues_text_widget.delete(1.0, tk.END)
        self.stats_text_widget.insert(tk.END, self.stats_text)
        self.issues_text_widget.insert(tk.END, self.issues_text)

        # Switch frames
        self.upload_frame.pack_forget()
        self.result_frame.pack(fill="both", expand=True)

    def back_to_upload(self):
        self.result_frame.pack_forget()
        self.upload_frame.pack(fill="both", expand=True)


# Main application loop
root = tk.Tk()
app = DataAnalyzerApp(root)
root.geometry("700x600")
root.mainloop()
