# use command: pip install -e .
# to install and test it locally before you publish it
from datetime import datetime
import json
import os
import traceback
from zipfile import ZipFile

import pandas as pd
from distutils.dir_util import remove_tree
from predictnow import cert
from pandas import DataFrame, read_parquet

from .notifier import MLTrainingCompletedNotifier
# from .notifier_timer import MLTrainingCompletedNotifier
from .find_files_with_specific_extensions import find_files_with_specific_extensions
from uuid import uuid4
from typing import Dict
import requests
from werkzeug.datastructures import FileStorage

# TODO: change the host url to Apigee
# host_api = should call proxy API gee //authentication/authorization
# host = "http://127.0.0.1:8080"
import firebase_admin
from firebase_admin import credentials

from .predict_result import PredictResult
from .training_result import TrainingResult,Result


class PredictNowClient:
    def __init__(self, url, api_key):
        self.api_key = api_key
        self.host = url
        cred = credentials.Certificate(cert)
        if len(firebase_admin._apps) == 0:  # check if firebase is already init
            firebase_admin.initialize_app(cred)

    def create_model(self, username, model_name, params, hyp_dict={}):
        request_params = {
                "params": params,
                "hyp_dict": hyp_dict,
                "model_name": model_name,
                "username": username,  # TODO replace with self.username
            }

        url = self.host + "/models"

        response = requests.post(
            url,
            json=request_params,
        )

        #returning model name in response
        response = json.loads(response.content.decode('utf-8'))
        response.update({"model_name":model_name})
        return response
    

    def features(self):
        """features list"""
        url = self.host + "/get_features"
        response = requests.get(url,)
        print(response)
        response = json.loads(response.content.decode('utf-8'))
        return response
    

    def get_price_features(self):
        """sharadar price features list"""
        url = self.host + "/get_price_features"
        response = requests.get(url,)
        print(response)
        response = json.loads(response.content.decode('utf-8'))
        return response
    
    def search_ticker(self,ticker_name):
        request_params = {
            "ticker_name":ticker_name
        }
        url = self.host + "/search_tickers"
        response = requests.get(url,
            json=request_params)

        response = json.loads(response.content.decode('utf-8'))
        return response
    
    def get_dimensions(self):
        dim = ["ARQ","ARY","ART"]
        print(dim)
        return dim

    
    def sharadar(self,
                dataset: DataFrame,
                sha_params={"features":[],"tickers":[],"price_features":[],"dimensions":[]}
               ):
        
        """ SHARADAR_TYPES:
            1 - fundamental data
            2 - price data
            3 - both fundamental and price data 
        """
        
        if dataset.index.dtype != datetime:
            print(dataset)
            dataset = self.update_date_index(dataset)
            dataset.name ="sharadar_input"
            path = self.__df_to_parquet_file__(dataset)
        
        start_date = dataset.index[0].date().strftime('%Y-%m-%d')
        end_date = dataset.index[-1].date().strftime('%Y-%m-%d')

        sha_params["start_date"] = start_date
        sha_params["end_date"] = end_date
        print(sha_params)

        if (sha_params.get("features") and sha_params.get("tickers") and sha_params.get("dimensions")) and not sha_params.get("price_features"):
            """sharadar fundamental features only"""

            sha_params["sharadar_type"]="1"
            
        elif ( sha_params.get("price_features") and sha_params.get("tickers")) and not (sha_params.get("features") and sha_params.get("dimensions")):
            """sharadar price features only"""
            
            sha_params["sharadar_type"]=2
            
        elif sha_params.get("features") and sha_params.get("tickers") and sha_params.get("dimensions") and sha_params.get("price_features"):
            """sharadar both fundamental and price features"""

            sha_params["sharadar_type"]=3
            
        elif sha_params.get("ticker_col") and (sha_params.get("features") or sha_params.get("price_features")):
            if sha_params.get("features") and not sha_params.get("dimensions"):
                return {"success":False,
                        "message":"Kindly give dimension with features in order to apply sharadar fundamental data with multi-ticker!"}
        
        else:
            return {"success":False,
                    "message":"Kindly send the parameters correctly!"}
        
        parquet_file = open(path, 'rb')
        files = {
                'parquet': parquet_file
            }
        url = self.host + "/sharadar"

        response = requests.post(url,
            files = files,
            data=sha_params)

        response = json.loads(response.content.decode('utf-8'))
        print(response)
        return response

    def train(self,
              input_df: DataFrame,
              model_name: str,
              label: str,
              username: str,  # TODO remove
              email: str,  # TODO remove
              return_output: bool = True,
              external_feature: bool = False
              ):

        try:
            params = {
                'model_name': model_name,
                'train_id': str(uuid4()),
                'username': username,
                'email': email,
                'label': label,
                'sharadar' : external_feature
            }

            notifier = MLTrainingCompletedNotifier(
                params['username'], params['train_id'])

            print(external_feature)
            if external_feature in ["True","true","TRUE"] :

                url = self.host + "/trainings"
                response = requests.post(
                    url,
                    data=params,
                    timeout=3000,
                ) 

            else:

                print("in false")
                path = self.__df_to_parquet_file__(input_df)
                parquet_file = open(path, 'rb')
                files = {
                    'parquet': parquet_file
                }
            
                url = self.host + "/trainings"
                response = requests.post(
                    url,
                    files=files,
                    data=params,
                    timeout=3000,
                )  # prevents TaskCancelled error
                print("return_op",return_output)
                    
                
            #returning model name in response
            response = json.loads(response.content.decode('utf-8'))
            
            return response

        except Exception as e:
            the_error_type = type(e).__name__
            the_traceback = traceback.format_exc()
            print(the_traceback)
            return {
                "success": False,
                "message": the_error_type + ": " + str(e),
            }

    def getstatus(self, 
                  username: str,
                  train_id: str):

        notifier = MLTrainingCompletedNotifier(
                username, train_id)
        result=notifier.wait_for_result()
       
        return result


    def predict(self,
                input_df: DataFrame,
                model_name: str,
                username: str,  # TODO remove
                eda: str = "no",
                prob_calib: str = "no",
                ) -> PredictResult:
        
        params = {
            'model_name': model_name,
            'username': username,
            'eda': eda,
            'prob_calib' : prob_calib
        }
        
        if input_df.index.dtype != datetime:
            input_df = self.update_date_index(input_df)
            input_df.name ="sharadar_live_input"

        path = self.__df_to_parquet_file__(input_df)
        parquet_file = open(path, 'rb')
        files = {
            'parquet': parquet_file
        }
        

        url = self.host + "/predictions"
        response = requests.post(
            url,
            data=params,
            files=files,
        )
       
        response = json.loads(response.content.decode('utf-8'))
        return PredictResult(
            title=response["title"],
            prob_calib=response["prob_calib"],
            filename=response["filename"],
            objective=response["objective"],
            eda=response["eda"],
            too_many_nulls_list=response["too_many_nulls_list"],
            suffix=response["suffix"],
            labels=response["labels"],
            probabilities=response["probabilities"],
        )

    def update_date_index(self, df):
        """
        search for word 'Date' with uppercase/lowercase variants. If we find it, then set index to that column. if not,
        use default index
        """
        date_name = ['Date', 'DATE', 'date', 'TIME', 'time', 'Time', '<Date>', '<date>', '<DATE>']
        for name in (df.columns.to_list()):
            if name in date_name:
                df = df.dropna(axis=0, subset=[name])
                df = df.set_index(name)
                df.index=pd.to_datetime(df.index)
                print('The dataset will be indexed by column: ' + name)
        return df
    

    def get_subscription_details(self,
                username: str,  # TODO remove
                ) -> PredictResult:

        url = self.host + "/get_subscription_details/" + username
        response = requests.get(
            url,
        )
        response = json.loads(response.content.decode('utf-8'))
        return response

    def get_account_status(self,
                username: str,  # TODO remove
                ) -> PredictResult:

        url = self.host + "/get_account_status/" + username
        response = requests.get(
            url,
        )
        response = json.loads(response.content.decode('utf-8'))
        return response

    def download_files(self,
                       username: str,
                       output_path: str = None,
                       model_name: str = "",
                       do_not_extract: bool = False,
                       ):
        """
	Download all your trained files in form of json
	"""
        
        output_path = output_path if output_path else os.getcwd()
        url = self.host + "/download_files"

        params = {
            'username': username,
            'model_name': model_name
        }
        response = requests.post(
            url,
            data=params,
        )
        response = response.content

        zip_path = os.path.join(output_path, params["username"] + ".zip")
        file = open(zip_path, "wb")
        file.write(response)
        file.close()

        message = "The result " + params["username"] + ".zip has been saved into " + output_path
        if not do_not_extract:
            message += " and extracted with the parquet files converted to CSV"
            with ZipFile(zip_path, 'r') as zipObj:
                zipObj.extractall(output_path)

            parquet_paths = find_files_with_specific_extensions(os.path.join(output_path, "userprofile_api"), "parquet")
            for parquet_path in parquet_paths:
                df = read_parquet(parquet_path)
                csv_path = parquet_path[:-8] + ".csv"
                df.to_csv(csv_path)

        return {
            "success": True,
            "message": message,
        }
    
    
    def getresult(self, 
                  model_name: str,
                  username: str):

        """
	method to get csv files and convert it to object
	"""
        
        url = self.host + "/get_result"
        
        params = {
            'username': username,
            'model_name': model_name
        }

        response = requests.post(
            url,
            data=params,
        )
       
        response = json.loads(response.content.decode('utf-8'))
       
        result= Result(
            success=True,
            lab_test = response["lab_test_"],
            feature_importance=response["feature_importance"],
            performance_metrics = response["performance_metrics"],
            predicted_prob_cv= response["predicted_prob_cv_"],
            predicted_prob_test= response["predicted_prob_test_"],
            predicted_targets_cv= response["predicted_targets_cv_"],
            predicted_targets_test= response["predicted_targets_test_"],
            eda_describe = response["eda_describe"]
        )
        return result

    def delete_files(self,
                       username: str,
                       model_name: str = "",
                       delete_all: bool = False,
                       ):
        """
        for deleting files and folders as per user's requirements
        """
        url = self.host + "/delete_files"

        params = {
            'username': username,
            'model_name': model_name,
            'delete_all': delete_all,
        }
        response = requests.post(
            url,
            data=params,
        )
        response = json.loads(response.content.decode('utf-8'))
        return response

    
    def __df_to_parquet_file__(self, input_df: DataFrame):
        df_name = self.__pick_name_from_df__(input_df)
        os.makedirs("temp", exist_ok=True)
        parquet_path = os.path.join("temp", df_name + ".parquet")
        input_df.to_parquet(parquet_path)

        return parquet_path  # TODO dont store the files, do it in mem?

    def __pick_name_from_df__(self, input_df: DataFrame):
        if hasattr(input_df, "name") and input_df.name:
            return input_df.name
        print("DF HAS NO NAME, USING A UUID. Assign a name to it e.g df.name = 'myfirstname'")
        if hasattr(input_df, "filename") and input_df.filename:
            return input_df.filename
        return str(uuid4())

    
