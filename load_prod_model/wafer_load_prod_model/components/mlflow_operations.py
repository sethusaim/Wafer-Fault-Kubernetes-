import logging
import sys
from os import environ

from mlflow import get_experiment_by_name, search_runs, set_tracking_uri
from mlflow.tracking import MlflowClient

from wafer_load_prod_model.components.s3_operations import S3Operation
from wafer_load_prod_model.exception import WaferException
from wafer_load_prod_model.utils.main_utils import MainUtils
from wafer_load_prod_model.utils.read_params import read_params


class MLFlowOperation:
    """
    Description :    This class shall be used for handling all the mlflow operations
    Version     :   1.2
    
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.config = read_params()

        self.mlflow_config = self.config["mlflow_config"]

        self.log_writer = logging.getLogger(__name__)

        self.s3 = S3Operation()

        self.utils = MainUtils()

        self.remote_server_uri = environ["MLFLOW_TRACKING_URI"]

        self.client = MlflowClient(self.remote_server_uri)

    def set_mlflow_tracking_uri(self):
        """
        Method Name :   set_mlflow_tracking_uri
        Description :   This method sets the mlflow tracking uri in mlflow server 
        
        Output      :   MLFLow server will set the particular uri to communicate with code 
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info(
            "Entered set_mlflow_tracking_uri method of MLFlowOperation class"
        )

        try:
            set_tracking_uri(self.remote_server_uri)

            self.log_writer.info("Set mlflow tracking uri")

            self.log_writer.info(
                "Exited set_mlflow_tracking_uri method of MLFlowOperation class"
            )

        except Exception as e:
            raise WaferException(e, sys) from e

    def get_experiment(self, exp_name):
        """
        Method Name :   get_experiment
        Description :   This method gets the experiment from mlflow server using the experiment name
        
        Output      :   An experiment which was stored in mlflow server
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info("Entered get_experiment method of MLFLowOperation class")

        try:
            exp = get_experiment_by_name(self.mlflow_config[exp_name])

            self.log_writer.info(f"Got {exp_name} experiment from mlflow")

            self.log_writer.info(
                "Exited get_experiment method of MLFLowOperation class"
            )

            return exp

        except Exception as e:
            raise WaferException(e, sys) from e

    def get_runs_from_mlflow(self, exp_id):
        """
        Method Name :   get_runs_from_mlflow
        Description :   This method gets the runs from the mlflow server for a particular experiment id
        
        Output      :   A pandas series object consisting of runs for the particular experiment id
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info(
            "Entered get_runs_from_mlflow method of MLFlowOperation class"
        )

        try:
            runs = search_runs(exp_id)

            self.log_writer.info(
                f"Completed searching for runs in mlflow with experiment ids as {exp_id}",
            )

            self.log_writer.info(
                "Exited get_runs_from_mlflow method of MLFlowOperation class"
            )

            return runs

        except Exception as e:
            raise WaferException(e, sys) from e

    def get_mlflow_models(self):
        """
        Method Name :   get_mlflow_models
        Description :   This method gets the registered models in mlflow server
        
        Output      :   A list of registered model names stored in mlflow server
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info(
            "Entered get_mlflow_models method of MLFlowOperation class"
        )

        try:
            reg_model_names = [rm.name for rm in self.client.list_registered_models()]

            self.log_writer.info("Got registered models from mlflow")

            self.log_writer.info(
                "Exited get_mlflow_models method of MLFlowOperation class"
            )

            return reg_model_names

        except Exception as e:
            raise WaferException(e, sys) from e

    def search_mlflow_models(self, order):
        """
        Method Name :   search_mlflow_models
        Description :   This method searches for registered models and returns them in the mentioned order
        
        Output      :   A list of registered models in the mentioned order
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info(
            "Entered search_mlflow_models method of MLFlowOperation class"
        )

        try:
            results = self.client.search_registered_models(order_by=[f"name {order}"])

            self.log_writer.info(f"Got registered models in mlflow in {order} order")

            self.log_writer.info(
                "Exited search_mlflow_models method of MLFlowOperation class"
            )

            return results

        except Exception as e:
            raise WaferException(e, sys) from e

    def transition_mlflow_model(
        self, model_version, stage, model_name, from_bucket, to_bucket
    ):
        """
        Method Name :   transition_mlflow_model
        Description :   This method transitions mlflow model from one stage to other stage, and does the same in s3 bucket
        
        Output      :   A mlflow model is transitioned from one stage to another, and same is reflected in s3 bucket
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info(
            "Entered transition_mlflow_model method of MLFlowOperation class"
        )

        try:
            current_version = model_version

            self.log_writer.info(f"Got {current_version} as the current model version")

            train_model_file = self.utils.get_model_file("trained_model", model_name)

            stag_model_file = self.utils.get_model_file("stag_model", model_name)

            prod_model_file = self.utils.get_model_file("prod_model", model_name)

            self.log_writer.info("Created trained,stag and prod model files")

            if stage == "Production":
                self.log_writer.info(f"{stage} is selected for transition")

                self.client.transition_model_version_stage(
                    model_name, current_version, stage
                )

                self.log_writer.info(f"Transitioned {model_name} to {stage} in mlflow")

                self.s3.copy_data(
                    train_model_file, from_bucket, prod_model_file, to_bucket,
                )

            elif stage == "Staging":
                self.log_writer.info(f"{stage} is selected for transition")

                self.client.transition_model_version_stage(
                    model_name, current_version, stage
                )

                self.log_writer.info(f"Transitioned {model_name} to {stage} in mlflow")

                self.s3.copy_data(
                    train_model_file, from_bucket, stag_model_file, to_bucket,
                )

            else:
                self.log_writer.info("Please select stage for model transition")

            self.log_writer.info(
                "Exited transition_mlflow_model method of MLFlowOperation class"
            )

        except Exception as e:
            raise WaferException(e, sys) from e

    def transition_best_models(self, model, top_models):
        """
        Method Name :   transition_best_models
        Description :   This method transitions the models to staging or production based on the condition nad moves the models within
                        s3 buckets also.
        
        Output      :   A list of registered models in the mentioned order
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info(
            "Entered transition_best_models method of MLFlowOperation class"
        )

        try:
            self.log_writer.info(
                "Started transitioning best models to production and rest to staging",
            )

            if model.name in top_models:
                self.transition_mlflow_model(
                    model.version, "Production", model.name, "model", "model"
                )

            ## In the registered models, even kmeans model is present, so during Prediction,
            ## this model also needs to be in present in production, the code logic is present below

            elif "KMeans" in model.name:
                self.transition_mlflow_model(
                    model.version, "Production", model.name, "model", "model"
                )

            else:
                self.transition_mlflow_model(
                    model.version, "Staging", model.name, "model", "model"
                )

            self.log_writer.info(
                "Transitioned best models to production and rest to staging",
            )

            self.log_writer.info(
                "Exited transition_best_models method of MLFlowOperation class"
            )

        except Exception as e:
            raise WaferException(e, sys) from e

    def get_best_models(self, runs, num_clusters):
        """
        Method Name :   get_best_models
        Description :   This method get the best models from the runs dataframe and based on the number of clusters
        
        Output      :   A list of registered models in the mentioned order
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        self.log_writer.info("Entered get_best_models method of MLFlowOperation class")

        try:
            reg_model_names = self.get_mlflow_models()

            cols = [
                "metrics." + str(model) + "-best_score"
                for model in reg_model_names
                if model != "KMeans"
            ]

            self.log_writer.info("Created cols list based on registered models")

            runs_cols = runs.filter(cols).max().sort_values(ascending=False)

            self.log_writer.info(
                "Filtered the runs dataframe based on the cols in descending order",
            )

            metrics_dict = runs_cols.to_dict()

            self.log_writer.info("Converted runs_cols to dict")

            """ 
                        Eg-output: For 3 clusters, 
                            [
                            metrics.XGBoost0-best_score,
                            metrics.XGBoost1-best_score,
                            metrics.XGBoost2-best_score,
                            metrics.RandomForest0-best_score,
                            metrics.RandomForest1-best_score,
                            metrics.RandomForest2-best_score
                        ] 

                        Eg- runs_dataframe: I am only showing for 3 cols,actual runs dataframe will be different
                                            based on the number of clusters
                                    since for every run cluster values changes, rest two cols will be left as blank,
                            so only we are taking the max value of each col, which is nothing but the value of the metric
                            

            run_number  metrics.XGBoost0-best_score metrics.RandomForest1-best_score metrics.XGBoost1-best_score
                0                   1                       0.5
                1                                                                                   1             2                                                                               """

            top_mn_lst = [
                max(
                    [
                        (file, metrics_dict[file])[0]
                        .split(".")[1]
                        .split("-best_score")[0]
                        for file in metrics_dict
                        if str(i)
                        in file.split(".")[1].split("-best_score")[0].split("-")[-1]
                    ]
                )
                for i in range(0, num_clusters)
            ]

            self.log_writer.info(
                "Got the best metric names from the metrics_dict and number of clusters",
            )

            ## best_metrics will store the value of metrics, but we want the names of the models,
            ## so best_metrics.index will return the name of the metric as registered in mlflow

            ## Eg. metrics.XGBoost1-best_score

            ## top_mn_lst - will store the top 3 model names

            self.log_writer.info("Got the top model list from best_metrics names")

            self.log_writer.info(
                "Exited get_best_models method of MLFlowOperation class"
            )

            return top_mn_lst

        except Exception as e:
            raise WaferException(e, sys) from e
