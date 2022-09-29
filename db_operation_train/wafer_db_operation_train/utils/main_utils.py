from shutil import rmtree
from datetime import datetime

from wafer_db_operation_train.components.s3_operations import S3_Operation

from utils.logger import AppLogger
from utils.read_params import get_log_dic, read_params


class MainUtils:
    """
    Description :   This class is used for main utility functions required in core functions of the service
    Version     :   1.2
    
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.s3 = S3_Operation()

        self.log_writer = AppLogger()

        self.config = read_params()

        self.current_date = f"{datetime.now().strftime('%Y-%m-%d')}"

        self.log_dir = self.config["dir"]["log"]

        self.files = self.config["files"]

        self.mongodb_config = self.config["mongodb"]

    def upload_logs(self):
        """
        Method Name :   upload_logs
        Description :   This method uploads the logs to s3 bucket
        
        Output      :   The logs are uploaded to s3 bucket
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__, self.upload_logs.__name__, __file__, "upload"
        )

        self.log_writer.info("start",)

        try:
            self.s3.upload_folder(
                self.log_dir, "logs",
            )

            self.log_writer.info(f"Uploaded logs to logs bucket",)

            self.log_writer.info("exit",)

            self.log_writer.stop_log()

            rmtree(self.log_dir)

        except Exception as e:
            self.log_writer.info(e,)

    def get_file_with_timestamp(self, file, log_file):
        """
        Method Name :   get_file_with_timestamp
        Description :   This method gets the file name with current time stamp
        
        Output      :   The filename is returned based on te current time stmap
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_file_with_timestamp.__name__,
            __file__,
            log_file,
        )

        self.log_writer.info("start",)

        try:
            file = self.current_date + "-" + self.files[file]

            self.log_writer.info("Got file name with date time stamp",)

            self.log_writer.info("exit",)

            return file

        except Exception as e:
            self.log_writer.info(e,)

    def get_collection_with_timestamp(self, collection_name, log_file):
        """
        Method Name :   get_collection_with_timestamp
        Description :   This method gets the collection name with current time stamp
        
        Output      :   The collection name is returned based on te current time stmap
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        log_dic = get_log_dic(
            self.__class__.__name__,
            self.get_collection_with_timestamp.__name__,
            __file__,
            log_file,
        )

        self.log_writer.info("start",)

        try:
            current_collection_name = (
                self.current_date + "-" + self.mongodb_config[collection_name]
            )

            self.log_writer.info("Got collection name with current time stamp",)

            self.log_writer.info("exit",)

            return current_collection_name

        except Exception as e:
            self.log_writer.info(e,)