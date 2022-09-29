import logging
import sys

from wafer_preprocess_pred.components.s3_operations import S3Operation
from wafer_preprocess_pred.exception import WaferException
from wafer_preprocess_pred.utils.main_utils import MainUtils


class DataGetterPred:
    """
    Description :   This class shall be used for obtaining the df from the input files s3 bucket where the training file is present
    Version     :   1.2
    
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.utils = MainUtils()

        self.s3 = S3Operation()

        self.log_writer = logging.getLogger(__name__)

    def get_data(self):
        """
        Method Name :   get_data
        Description :   This method reads the data from the input files s3 bucket where the training file is stored
        
        Output      :   A pandas dataframe
        On Failure  :   Write an exception log and then raise exception    
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info("Entered the get_data method of DataGetterPred class")

        try:
            ip_fname = self.utils.get_file_with_timestamp("pred_export")

            df = self.s3.read_csv(ip_fname, "feature_store", fidx=True)

            self.log_writer.info("Prediction data loaded from feature store bucket")

            self.log_writer.info("Exited the get_data method of DataGetterPred class")

            return df

        except Exception as e:
            raise WaferException(e, sys) from e
