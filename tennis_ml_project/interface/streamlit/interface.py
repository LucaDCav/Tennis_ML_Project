import streamlit as st
import pandas as pd
import requests
import os


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
        tennis_api_url = 'http://localhost:8000/predict'
        response = requests.get(tennis_api_url, params=params)
        result = response.json()
        del round
        prob = round(result[1] * 100, 2)
        test = ""

        if result[0] == "Player 2 wins":
            test = f"{player_2[9:]} wins with {prob}%"
        elif result[0] == "Player 1 wins":
            test = f"{player_1[9:]} wins with {prob}%"
        else:
            test = "Draw"

        st.success(test)
    else:
        st.error("Please select both players before starting the match.")
