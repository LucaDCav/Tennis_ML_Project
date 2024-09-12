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

    if float(result[0][0]) > float(result[0][1]):
        player = "Player 2 wins"
        prob = float(result[0][0])
        return player, prob

    if float(result[0][0]) < float(result[0][1]):
        player = "Player 1 wins"
        prob = float(result[0][1])
        return player, prob
    else:
        return "Draw"

    # $CHA_END


@app.get("/")
def root():
    # $CHA_BEGIN
    return dict(greeting="Hello")
    # $CHA_END
