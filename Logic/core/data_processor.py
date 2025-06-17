import pandas as pd
import os


class DataProcessor:
    def __init__(self):
        self.uploaded_file = None
        self.processed_data = []
        self.dataframe = None

    def load_file(self, file_path):
        # load and process the uploaded file
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")

            self.uploaded_file = file_path
            self.dataframe = df
            self.processed_data = df.to_dict("records")

            return True, f"File loaded successfully! {len(df)} records found."

        except Exception as e:
            return False, f"Failed to load file: {str(e)}"

    def get_data_preview(self, max_rows=20):
        # get preview of the loaded data
        if self.dataframe is not None:
            return self.dataframe.head(max_rows)
        return None

    def get_file_info(self):
        # get information about the loaded file
        if self.uploaded_file:
            filename = os.path.basename(self.uploaded_file)
            record_count = len(self.processed_data)
            return f"File: {filename} ({record_count} records)"
        return "No file selected"

    def has_data(self):
        return len(self.processed_data) > 0

    def get_record_count(self):
        return len(self.processed_data)

    def get_processed_data(self):
        return self.processed_data
