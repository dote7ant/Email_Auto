import pandas as pd
import os
import re


class DataProcessor:
    def __init__(self):
        self.uploaded_file = None
        self.processed_data = []
        self.dataframe = None
        self.raw_dataframe = None  # store original data for reference

    def preprocess_data(self, data):

        # create a copy to avoid modifying the original data
        processed_data = data.copy()

        # Rename columns to standardize naming
        column_mapping = {
            "off the job": "off_the_job",
            "Off the job": "off_the_job",
            "Off the Job": "off_the_job",
            "Off The Job": "off_the_job",
            "Last attended": "last_attended",
            "Last Attended": "last_attended",
            "last attended": "last_attended",
            "Apprentice": "first_name",
        }

        processed_data.rename(columns=column_mapping, inplace=True)

        # ensure required columns exist
        required_columns = ["off_the_job", "last_attended", "First Name"]
        for col in required_columns:
            if col not in processed_data.columns:
                print(f"Warning: Column '{col}' not found. Creating empty column.")
                processed_data[col] = 0

        # remove non-digit characters and clean data
        processed_data["off_the_job"] = (
            processed_data["off_the_job"].astype(str).str.replace(r"\D", "", regex=True)
        )
        processed_data["last_attended"] = (
            processed_data["last_attended"]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
        )

        # convert to numeric, fill NaN, and convert to int
        processed_data["off_the_job"] = (
            pd.to_numeric(processed_data["off_the_job"], errors="coerce")
            .fillna(0)
            .astype(int)
        )
        processed_data["last_attended"] = (
            pd.to_numeric(processed_data["last_attended"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

        # apply categorization
        processed_data["off_track_category"] = processed_data.apply(
            lambda row: self.categorize_off_the_job(
                row["off_the_job"], row["last_attended"]
            ),
            axis=1,
        )

        processed_data["hours_behind"] = processed_data[
            "off_the_job"
        ]  # alias for template compatibility
        processed_data["days_absent"] = processed_data[
            "last_attended"
        ]  # alias for template compatibility

        if "email" not in processed_data.columns:
            processed_data["email"] = ""

        return processed_data

    def categorize_off_the_job(self, hrs, dys):
        try:
            hrs = int(hrs) if hrs else 0
            dys = int(dys) if dys else 0
        except (ValueError, TypeError):
            hrs = 0
            dys = 0

        if hrs >= 30 and dys > 30:
            return "significantly"
        elif hrs >= 15:
            return "moderately"
        elif hrs > 10:
            return "slightly"
        else:
            return "on_track"

    def load_file(self, file_path):
        try:
            # load the file
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")

            # store raw data
            self.raw_dataframe = df.copy()

            # preprocess the data
            self.dataframe = self.preprocess_data(df)

            # update processed_data list
            self.processed_data = self.dataframe.to_dict("records")
            self.uploaded_file = file_path

            return (
                True,
                f"File loaded and processed successfully! {len(self.dataframe)} records found.",
            )

        except Exception as e:
            return False, f"Failed to load file: {str(e)}"

    def get_data_preview(self, max_rows=20):
        if self.dataframe is not None:
            return self.dataframe.head(max_rows)
        return None

    # def get_raw_data_preview(self, max_rows=20):
    #     if self.raw_dataframe is not None:
    #         return self.raw_dataframe.head(max_rows)
    #     return None

    def get_file_info(self):
        if self.uploaded_file:
            filename = os.path.basename(self.uploaded_file)
            record_count = len(self.processed_data)
            return f"File: {filename} ({record_count} records)"
        return "No file selected"

    # def get_category_summary(self):
    #     """Get summary of categories in the processed data"""
    #     if not self.has_data():
    #         return {}

    #     category_counts = {}
    #     for record in self.processed_data:
    #         category = record.get("off_track_category", "unknown")
    #         category_counts[category] = category_counts.get(category, 0) + 1

    #     return category_counts

    # def get_detailed_summary(self):
    #     """get detailed summary including statistics"""
    #     if not self.has_data():
    #         return "No data loaded"

    #     summary = []
    #     summary.append(f"Total Records: {len(self.processed_data)}")
    #     summary.append("")

    #     category_counts = self.get_category_summary()
    #     summary.append("Category Breakdown:")

    #     category_labels = {
    #         "significantly": "Significantly Off-Track",
    #         "moderately": "Moderately Off-Track",
    #         "slightly": "Slightly Off-Track",
    #         "on_track": "On Track",
    #     }

    #     for category, count in category_counts.items():
    #         percentage = (count / len(self.processed_data)) * 100
    #         label = category_labels.get(category, category.replace("_", " ").title())
    #         summary.append(f"  {label}: {count} ({percentage:.1f}%)")

    #     summary.append("")

    #     # statistics
    #     if self.dataframe is not None:
    #         summary.append("Statistics:")
    #         summary.append(
    #             f"  Average hours behind: {self.dataframe['off_the_job'].mean():.1f}"
    #         )
    #         summary.append(f"  Max hours behind: {self.dataframe['off_the_job'].max()}")
    #         summary.append(
    #             f"  Average days since attendance: {self.dataframe['last_attended'].mean():.1f}"
    #         )
    #         summary.append(
    #             f"  Max days since attendance: {self.dataframe['last_attended'].max()}"
    #         )

    #     return "\n".join(summary)

    def has_data(self):
        # check if data is loaded
        return len(self.processed_data) > 0

    def get_record_count(self):
        # get total number of records
        return len(self.processed_data)

    def get_processed_data(self):
        # get the processed data as list of dictionaries
        return self.processed_data

    def get_dataframe(self):
        """Get the processed data as pandas DataFrame"""
        return self.dataframe

    # def get_raw_dataframe(self):
    #     """Get the original unprocessed data as pandas DataFrame"""
    #     return self.raw_dataframe

    def get_category_data(self, category):
        if not self.has_data():
            return []

        return [
            record
            for record in self.processed_data
            if record.get("off_track_category") == category
        ]

    # def export_processed_data(self, file_path):
    #     try:
    #         if self.dataframe is None:
    #             return False, "No data to export"

    #         if file_path.endswith(".csv"):
    #             self.dataframe.to_csv(file_path, index=False)
    #         elif file_path.endswith(".xlsx"):
    #             self.dataframe.to_excel(file_path, index=False)
    #         else:
    #             return False, "Unsupported export format"

    #         return True, f"Data exported successfully to {file_path}"

    #     except Exception as e:
    #         return False, f"Failed to export data: {str(e)}"

    # def auto_export(self, directory="~/Logic/loaded_data.xlsx"):
    #     if not self.has_data():
    #         return False, "No data to export"

    #     file_path = os.path.join(directory, "processed_data.csv")
    #     return self.export_processed_data(file_path)

    def reprocess_data(self):
        # reprocess the raw data
        if self.raw_dataframe is None:
            return False, "No raw data available to reprocess"

        try:
            self.dataframe = self.preprocess_data(self.raw_dataframe)
            self.processed_data = self.dataframe.to_dict("records")
            return True, "Data reprocessed successfully"

        except Exception as e:
            return False, f"Failed to reprocess data: {str(e)}"

    # TODO: data Retrieval - Enhanced with preprocessing
    def search_records(self, **kwargs):
        # search records based on criteria
        if not self.has_data():
            return []

        results = self.processed_data.copy()

        for key, value in kwargs.items():
            if key in ["off_the_job", "last_attended"]:
                # numeric search
                results = [r for r in results if r.get(key, 0) >= value]
            else:
                # string search (case insensitive)
                results = [
                    r
                    for r in results
                    if str(value).lower() in str(r.get(key, "")).lower()
                ]

        return results

    # TODO: email Data Enrichment - Enhanced with category-based enrichment
    def enrich_email_data(self, additional_data_dict):
        # enrich existing records with additional data
        if not self.has_data():
            return False, "No data to enrich"

        try:
            for record in self.processed_data:
                email = record.get("email", "")
                if email in additional_data_dict:
                    record.update(additional_data_dict[email])

            # update dataframe
            self.dataframe = pd.DataFrame(self.processed_data)

            return True, f"Data enriched for {len(additional_data_dict)} records"

        except Exception as e:
            return False, f"Failed to enrich data: {str(e)}"
