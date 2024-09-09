import streamlit as st
import pandas as pd
import requests


def parse_age_range(age_range):
    if age_range == '- 20':
        return 0, 20
    elif age_range == '41 +':
        return 41, 65
    else:
        return map(int, age_range.split('~'))

df = pd.read_csv("player_df.csv")
df[['age_min', 'age_max']] = df['age'].apply(lambda x: pd.Series(parse_age_range(x)))

# Set page configuration (title and icon)
st.set_page_config(page_title="🎾 Tennis Match Simulator", page_icon="🎾")

# CSS to add background color and font changes
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f3f0;
        font-family: 'Helvetica', sans-serif;
    }
    h1 {
        color: #001f3f;
        font-size: 3rem;
    }

    h3 {
        color: #001f3f;

    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title with emojis
st.title("🎾 Welcome to the Tennis Match Simulator 🏆")

# Add a fun subheader
st.subheader("Who's going to win today? Let the match begin!")

# Use columns for a side-by-side layout for names and ages
col1, col2 = st.columns(2)


with col1:

    player_1 = st.selectbox("Choose name", options=df['player'].unique(), key=1)
    age1 = st.slider("Player 1 Age", int(df[(df["player"] == player_1)]['age_min'].iloc[0]), int(df[(df["player"] == player_1)]['age_max'].iloc[-1]))

with col2:
    player_2 = st.selectbox("Choose name", options=df['player'].unique(), key=2)
    age2 = st.slider("Player 2 Age", int(df[(df["player"] == player_2)]['age_min'].iloc[0]), int(df[(df["player"] == player_2)]['age_max'].iloc[-1]))

# Dropdown to select surface type with tennis court images
surface = st.selectbox(
    "Surface Type",
    ["Clay", "Grass", "Hard"],
)

minutes = st.selectbox(
    "Duration of the match:",
    [60, 120, 180]
)

round = st.selectbox(
    "Match round:",
    ['F', 'SF', 'QF','R16', 'R32', 'R64', 'R128']
)

draw_size = st.selectbox(
    "Championship draw size:",
    [16, 32, 64, 128]
)

best_of = st.selectbox(
    "Match best of:",
    [3, 5]
)




# Button to start the match
if st.button("🏁 Start Match"):
    params= {
    #    "player_1_name": player_1,
    #   "player_2_name": player_2,
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

    st.write(result)

    #st.success(f"Simulating match between {player_1} and {player_2} on {surface} surface!")
