# predictnow-api

# TO BEGIN ANY WORK WITH PREDICTNOW.AI CLIENT, WE START BY IMPORTING AND CREATING A CLASS INSTANCE
    from predictnow.pdapi import PredictNowClient
    import pandas as pd

    api_key = "KeyProvidedToEachOfOurSubscriber"   
    api_host = "http://%VMIP%"  

    # Initial variables
    username = "user1"  
    email = "xxxx@gmail.com"
    client = PredictNowClient(api_host,api_key)

# YOU WILL NEED TO EDIT THIS INPUT DATASET FILE PATH, LABELNAME AND MODELNAME!
    file_path = 'my_amazing_features.xlsx'  
    labelname = 'futreturn' #might need to change this name accordingly 
    modelname = 'model1' # 
    import os

# NOW YOUR PREDICTNOW.AI CLIENT HAS BEEN SETUP.

    # For classification problem
    params = {"timeseries": "yes", "weights": "no", "prob_calib": "no", "eda": "no", "type": "classification", "feature_selection": "shap", "analysis": "small", "boost": "gbdt", "mode": "train", "testsize": "1"}

    # For regression problems
    params = {"timeseries": "yes", "weights": "no", "prob_calib": "no", "eda": "no", "type": "regression", "feature_selection": "shap", "analysis": "small", "boost": "gbdt", "mode": "train", "testsize": "1"}

    print("THE PARAMS", params)


# LET'S CREATE THE MODEL BY SENDING THE PARAMETERS TO PREDICTNOW.AI

    response = client.create_model
                       (
                        username=username, # only letters, numbers, or underscores
                        model_name=modelname,
                        params=params,
                       )

    print(response)


# LET'S LOAD UP THE FILE TO PANDAS IN THE LOCAL ENVIRONMENT

    from pandas import read_csv  # If you have the Excel file, replace read_csv with read_excel
    from pandas import read_excel
    df = read_excel(file_path)  # Same here
    df.name = "testdataframe"  # Optional, but recommended

    print(df)

# START TRAINING MODEL
# NOTE: THIS MAY TAKE UP TO several minutes
    response = client.train
                        (
                            model_name=modelname,
                            input_df=df,
                            label=labelname,
                            username=username,
                            email=email,
                            return_output=False
                        )

    print("THE CLIENT HAS SENT THE DATASET TO THE SERVER AND TRIGGERED THE TRAINING MODEL TASK")
    print(response)

# CHECK THE STATUS OF THE MODEL
    status = client.getstatus(
                                username=username,
                                train_id=response["train_id"]
                             )

    print("Current status:")
    print(status)

#  NOW WE WILL DOWNLOAD FILES

    if status["state"] == "COMPLETED":

        response = client.getresult(
            model_name=modelname,
            username=username,
        )

        import pandas as pd
        predicted_prob_cv = pd.read_json(response.predicted_prob_cv)
        print("predicted_prob_cv")
        print(predicted_prob_cv)

        predicted_prob_test = pd.read_json(response.predicted_prob_test)
        print("predicted_prob_test")
        print(predicted_prob_test)


        predicted_targets_cv = pd.read_json(response.predicted_targets_cv)
        print("predicted_targets_cv")
        print(predicted_targets_cv)

# START PREDICTING USING THE TRAINED MODEL
    if status["state"] == "COMPLETED":

        df = read_excel("example_input_live_latest.xlsx")
        df.name = "myfirstpredictname"  # optional, but recommended

        # Predict demo
        response = client.predict(
            model_name=modelname,
            input_df=df,
            username=username,
            eda=params["eda"],
            prob_calib=params["prob_calib"]
        )

