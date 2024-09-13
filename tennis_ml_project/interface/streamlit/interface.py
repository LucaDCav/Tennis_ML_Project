import streamlit as st
import pandas as pd
import requests
import os
import pickle
from google.cloud import storage


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

    BUCKET_NAME = "tennis_ml_bucket"

    storage_filename = "finalized_model.sav"
    local_filename = "finalized_model.sav"

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(storage_filename)
    blob.download_to_filename(local_filename)

    X_pred = pd.DataFrame(locals(), index=[0])

    print(X_pred)

    # load the model from disk
    filename = 'finalized_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    result = loaded_model.predict_proba(X_pred)

    if float(result[0][0]) > float(result[0][1]):
        return {"winner": "Player 2", "probability": float(result[0][0])}
    elif float(result[0][0]) < float(result[0][1]):
        return {"winner": "Player 1", "probability": float(result[0][1])}
    else:
        return {"result": "Draw"}


# Function to parse the age range
def parse_age_range(age_range):
    if age_range == '- 20':
        return 14, 20
    elif age_range == '41 +':
        return 41, 65
    else:
        return map(int, age_range.split('~'))

# Read the CSV file (modify the path if necessary)
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, 'player_df.csv')

df = pd.read_csv(csv_path)
df[['age_min', 'age_max']] = df['age'].apply(lambda x: pd.Series(parse_age_range(x)))

# Configure the page (title and icon)
st.set_page_config(page_title="🎾 Tennis Match Simulator", page_icon="🎾")

# Function to load custom CSS
def load_css(filename):
    with open(filename, "r") as f:
        css = f.read()
    return css

# Load the CSS
style_path = os.path.join(current_dir, 'style.css')

css = load_css(style_path)
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Title with emojis
st.title("🎾 Welcome to the Tennis Match Simulator 🏆")

# Fun subtitle
st.subheader("Who's going to win today? Let the match begin!")

# Use columns for side-by-side layout for player names and ages
col1, col2 = st.columns(2)

with col1:
    # Add a placeholder "Select Player" in the selectbox
    player_1 = st.selectbox("Choose Player 1", options=["Select Player 1"] + list(df['player'].unique()), key=1)

    # Check if a player has been selected before showing the age slider
    if player_1 != "Select Player 1":
        age1 = st.slider("Age of Player 1",
                         int(df[(df["player"] == player_1)]['age_min'].iloc[0]),
                         int(df[(df["player"] == player_1)]['age_max'].iloc[-1]))
    else:
        age1 = None

with col2:
    # Add a placeholder "Select Player" in the selectbox
    player_2 = st.selectbox("Choose Player 2", options=["Select Player 2"] + list(df['player'].unique()), key=2)

    # Check if a player has been selected before showing the age slider
    if player_2 != "Select Player 2":
        age2 = st.slider("Age of Player 2",
                         int(df[(df["player"] == player_2)]['age_min'].iloc[0]),
                         int(df[(df["player"] == player_2)]['age_max'].iloc[-1]))
    else:
        age2 = None

# Dropdown to select the surface type
surface = st.selectbox(
    "Surface Type",
    options=["Select Surface"] + ["Clay", "Grass", "Hard"],
)

# Dropdown to select the game duration
minutes = st.selectbox(
    "Game Duration:",
    options=["Select Duration"] + [60, 120, 180]
)

# Dropdown to select the match round
round = st.selectbox(
    "Match Round:",
    options=["Select Round"] + ['F', 'SF', 'QF', 'R16', 'R32', 'R64', 'R128']
)

# Dropdown to select the tournament draw size
draw_size = st.selectbox(
    "Tournament Draw Size:",
    options=["Select Size"] + [16, 32, 64, 128]
)

# Dropdown to select the match format (best of 3 or 5)
best_of = st.selectbox(
    "Best of:",
    [3, 5]
)

# Button to start the match
if st.button("🏁 Start Match"):
    if player_1 != "Select Player" and player_2 != "Select Player":
        params = {
            "player_1_age": age1,
            "player_2_age": age2,
            "round": round,
            "surface": surface,
            "minutes": minutes,
            "draw_size": draw_size,
            "best_of": best_of,
            "player_1_ht": float(df[df["player"] == player_1]['height'].iloc[0]),
            "player_2_ht": float(df[df["player"] == player_2]['height'].iloc[0]),
            'player_1_df': float(df[(df["player"] == player_1) & (df['age_min'] <= age1) & (age1 <= df['age_max'])]['df'].iloc[0]),
            'player_2_df': float(df[(df["player"] == player_2) & (df['age_min'] <= age2) & (age2 <= df['age_max'])]['df'].iloc[0]),
            'player_1_hand': df[df["player"] == player_1]['hand'].iloc[0],
            'player_2_hand': df[df["player"] == player_2]['hand'].iloc[0],
            'player_1_ace': float(df[(df["player"] == player_1) & (df['age_min'] <= age1) & (age1 <= df['age_max'])]['ace'].iloc[0]),
            'player_2_ace': float(df[(df["player"] == player_2) & (df['age_min'] <= age2) & (age2 <= df['age_max'])]['ace'].iloc[0]),
            'player_1_bpSaved': float(df[(df["player"] == player_1) & (df['age_min'] <= age1) & (age1 <= df['age_max'])]['bpSaved'].iloc[0]),
            'player_2_bpSaved': float(df[(df["player"] == player_2) & (df['age_min'] <= age2) & (age2 <= df['age_max'])]['bpSaved'].iloc[0]),
            'age_diff': abs(age2 - age1),
            'ht_diff': abs(float(df[df["player"] == player_2]['height'].iloc[0]) - float(df[df["player"] == player_1]['height'].iloc[0]))
        }
        result = predict(
            player_1_age = age1,
            player_2_age = age2,
            round = round,
            surface = surface,
            minutes = minutes,
            draw_size = draw_size,
            best_of = best_of,
            player_1_ht = float(df[df["player"] == player_1]['height'].iloc[0]),
            player_2_ht = float(df[df["player"] == player_2]['height'].iloc[0]),
            player_1_df = float(df[(df["player"] == player_1) & (df['age_min'] <= age1) & (age1 <= df['age_max'])]['df'].iloc[0]),
            player_2_df = float(df[(df["player"] == player_2) & (df['age_min'] <= age2) & (age2 <= df['age_max'])]['df'].iloc[0]),
            player_1_hand = df[df["player"] == player_1]['hand'].iloc[0],
            player_2_hand = df[df["player"] == player_2]['hand'].iloc[0],
            player_1_ace = float(df[(df["player"] == player_1) & (df['age_min'] <= age1) & (age1 <= df['age_max'])]['ace'].iloc[0]),
            player_2_ace = float(df[(df["player"] == player_2) & (df['age_min'] <= age2) & (age2 <= df['age_max'])]['ace'].iloc[0]),
            player_1_bpSaved = float(df[(df["player"] == player_1) & (df['age_min'] <= age1) & (age1 <= df['age_max'])]['bpSaved'].iloc[0]),
            player_2_bpSaved = float(df[(df["player"] == player_2) & (df['age_min'] <= age2) & (age2 <= df['age_max'])]['bpSaved'].iloc[0]),
            age_diff = abs(age2 - age1),
            ht_diff = abs(float(df[df["player"] == player_2]['height'].iloc[0]) - float(df[df["player"] == player_1]['height'].iloc[0]))
        )
        del round
        prob = round(result["probability"] * 100, 2)
        prediction_result = ""

        if result['winner'] == "Player 2":
            prediction_result = f"Player 2: {player_2[9:]} wins with {prob}%"
        elif result['winner'] == "Player 1":
            prediction_result = f"Player 1: {player_1[9:]} wins with {prob}%"
        else:
            prediction_result = "Draw"

        st.success(prediction_result)
    else:
        st.error("Please select both players before starting the match.")
