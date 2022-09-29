import logging
import sys

from exception import WaferException
from utils.read_params import read_params

from wafer_data_transform_train.components.s3_operations import S3Operation


class DataTransformTrain:
    """
    Description :   This class shall be used for transforming the good raw training data before loading it in database
    Version     :   1.2
    
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.config = read_params()

        self.s3 = S3Operation()

        self.log_writer = logging.getLogger(__name__)

        self.col = self.config["col"]

    def replace_missing_with_null(self):
        """
        Method Name :   replace_missing_with_null
        Description :   This method replaces the missing values with null values
        
        Output      :   The column name is renamed 
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info(
            "Entered replace_missing_with_null method of DataTransformTrain class"
        )

        try:
            lst = self.s3.read_csv_from_folder("train_good_data", "train_data")

            for _, f in enumerate(lst):
                df = f[0]

                file = f[1]

                abs_f = f[2]

                df.fillna("NULL", inplace=True)

                df["Wafer"] = df["Wafer"].str[6:]

                self.log_writer.info(
                    f"Replaced missing values with null for the file {file}"
                )

                self.s3.upload_df_as_csv(df, abs_f, file, "train_data")

            self.log_writer.info(
                "Exited replace_missing_with_null method of DataTransformTrain class"
            )

        except Exception as e:
            raise WaferException(e, sys) from e

    def rename_column(self, from_col, to_col):
        """
        Method Name :   rename_column
        Description :   This method renames the column name from from_col to_col
        
        Output      :   The column name is renamed 
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info("Entered rename_column method of DataTransformTrain class")

        try:
            lst = self.s3.read_csv_from_folder("train_good_data", "train_data")

            for _, f in enumerate(lst):
                df = f[0]

                file = f[1]

                abs_f = f[2]

                df.rename(columns={self.col[from_col]: self.col[to_col]}, inplace=True)

                self.log_writer.info(f"Renamed the output columns for the file {file}")

                self.s3.upload_df_as_csv(df, abs_f, file, "train_data")

            self.log_writer.start_log("exit",)

            self.log_writer.info(
                "Exited rename_column method of DataTransformTrain class"
            )

        except Exception as e:
            raise WaferException(e, sys) from e