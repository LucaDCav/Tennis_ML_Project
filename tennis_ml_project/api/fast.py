import pandas as pd
import pickle

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# $WIPE_BEGIN
# 💡 Preload the model to accelerate the predictions
# We want to avoid loading the heavy Deep Learning model from MLflow at each `get("/predict")`
# The trick is to load the model in memory when the Uvicorn server starts
# and then store the model in an `app.state.model` global variable, accessible across all routes!
# This will prove very useful for the Demo Day

# $WIPE_END

# http://127.0.0.1:8000/predict?pickup_datetime=2014-07-06+19:18:00&pickup_longitude=-73.950655&pickup_latitude=40.783282&dropoff_longitude=-73.984365&dropoff_latitude=40.769802&passenger_count=2
@app.get("/predict")
def predict(
        player_1_age,
        player_2_age,
        round,
        surface,
        minutes,
        draw_size,
        best_of,
        player_1_ht,
        player_2_ht,
        player_1_df,
        player_2_df,
        player_1_hand,
        player_2_hand,
        player_1_ace,
        player_2_ace,
        player_1_bpSaved,
        player_2_bpSaved,
        age_diff,
        ht_diff
    ):

    # $CHA_BEGIN

    X_pred = pd.DataFrame(locals(), index=[0])

    print(X_pred)

    # load the model from disk
    filename = 'finalized_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    result = loaded_model.predict_proba(X_pred)


    # ⚠️ fastapi only accepts simple Python data types as a return value
    # among them dict, list, str, int, float, bool
    # in order to be able to convert the api response to JSON
    return dict(loser=float(result[0][0]), winner= float(result[0][1]))
    # $CHA_END


@app.get("/")
def root():
    # $CHA_BEGIN
    return dict(greeting="Hello")
    # $CHA_END
