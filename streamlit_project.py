import pandas as pd
import numpy as np
import streamlit as st
from mplsoccer import VerticalPitch, Pitch
import mplcursors




# Load data
test_df = pd.read_csv("./test_data_shots.csv")

# Clean data
test_df['xG'] = test_df['xG'].fillna(0)
test_df['team'] = np.where(test_df["h_a"] == "h", test_df["h_team"], test_df["a_team"])
test_df = test_df[["id", "minute", "result", "X", "Y", "xG", "player", "team", "situation", "shotType", "match_id", "h_goals", "a_goals", "player_assisted", "lastAction", "date", "h_team", "a_team"]]
test_df = test_df.sort_values(by=['team', 'player'])



def filter_data(df: pd.DataFrame, team: str, player: str) -> pd.DataFrame:
    """
    Filters the data based on conditions selected by the user

    Parameters:
    - df (pd.DataFrame): the DataFrame to filter
    - team (str): the team to filter by
    - player (str): the player to filter by

    Returns:
    - pd.DataFrame: the filtered DataFrame

    """

    if team: 

        df = df[df["team"] == team] 

    if player and player != "": 

        df = df[df["player"] == player] 
    
    return df

def shots_plot(df: pd.DataFrame, ax, pitch):
    """
    Creates the plot of shots on the pitch 

    Parameters:
    - df (pd.DataFrame): the DataFrame to plot
    - ax: the axis to plot on
    - pitch: the pitch object to plot on

    Returns:
    - None: plots the shots!

    """

    ax.set_title("xG Plot")

    # Iterate through each record
    for x in df.to_dict(orient = "records"):

        pitch.scatter(
            x = 100 * x["X"],
            y = 100 * x["Y"],
            ax = ax,
            s = 1000 * x["xG"],
            color = "green" if x["result"] == "Goal" else "white",
            edgecolors = "black",
            alpha = 1 if x["result"] == "Goal" else 0.5,
            zorder = 2 if x["result"] == "Goal" else 1
        )



def get_plot_labels(df: pd.DataFrame) -> dict:
    """
    Gets the labels for the plot

    Parameters:
    - df (pd.DataFrame): the DataFrame to get labels for

    Returns:
    - plot_labels (dict): dictionary containing the labels for the plot

    """

    labels = {}

    # match_df = df[df["match_id"] == match_id]

    # Isolate home and away teams
    labels["home_team"] = df["h_team"].iloc[0]
    labels["away_team"] = df["a_team"].iloc[0]

    # Isolate date (crudely)
    labels["date"] = df["date"].iloc[0][0:10]

    return labels


# st.title(f"Tottenham vs. Nottingham Forest (2024-12-26)")

labels = get_plot_labels(test_df)

st.title(f"{labels["away_team"]} vs. {labels["home_team"]} ({labels["date"]})")
st.subheader("Filter to a team/player to see all of their shots in the game!")

# Ensure there is actually data available
if test_df.empty:
    st.error("No data available to display.")
    st.stop()

# Configure streamlit app
teams = test_df["team"].unique()

team = st.selectbox(
    label = "Select a team",
    options = test_df["team"].unique(),
    index = 0
)

# Isolate players to plot, add empty string to allow for all players, and sort
available_players = test_df[test_df["team"] == team]["player"].unique().tolist()
available_players.append("")
available_players.sort()

player = st.selectbox(
    label = "Select a player",
    options = available_players,
    index = 0
)

# Isolate data
xG_df = filter_data(test_df, team = team, player = player)

# Create a pitch
pitch = Pitch(pitch_type = "opta", line_zorder = 2, pitch_color = "#f0f0f0", line_color = "black", half = True)

fig, ax = pitch.draw(figsize=(10, 10))
shots_plot(xG_df, ax, pitch)

st.pyplot(fig)

