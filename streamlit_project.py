import pandas as pd
import numpy as np
import streamlit as st
from mplsoccer import VerticalPitch
import mplcursors


st.title("Tottenham vs. Nottingham Forest (2024-12-26)")
st.subheader("Filter to a team/player to see all of their shots in the game!")

# Load data
test_df = pd.read_csv("./test_data_shots.csv")

# Clean data
test_df['xG'] = test_df['xG'].fillna(0)
test_df['team'] = np.where(test_df["h_a"] == "h", test_df["h_team"], test_df["a_team"])
test_df = test_df[["id", "minute", "result", "X", "Y", "xG", "player", "team", "situation", "shotType", "match_id", "h_goals", "a_goals", "player_assisted", "lastAction", "date"]]
test_df = test_df.sort_values(by=['team', 'player'])


# Ensure there is actually data available
if test_df.empty:
    st.error("No data available to display.")
    st.stop()


def filter_data(df: pd.DataFrame, team: str, player: str):
    """
    """

    if team: 

        df = df[df["team"] == team] 

    if player and player != "": 

        df = df[df["player"] == player] 
    
    return df

def shots_plot(df: pd.DataFrame, ax, pitch):
    """
    """

    ax.set_title("xG Plot")
    scatter = []

    # Iterate through each record
    for x in df.to_dict(orient = "records"):

        shot = pitch.scatter(
            x = 100 * x["X"],
            y = 100 * x["Y"],
            ax = ax,
            s = 1000 * x["xG"],
            color = "green" if x["result"] == "Goal" else "white",
            edgecolors = "black",
            alpha = 1 if x["result"] == "Goal" else 0.5,
            zorder = 2 if x["result"] == "Goal" else 1
        )

        # Append to scatter (list of points)
        scatter.append(shot)

    # Enable interactive tooltips
    cursor = mplcursors.cursor(
        scatter,
        hover = True
    )
    
    @cursor.connect("add")
    def on_add(selection):
        """
        """
        shot_data = df.iloc[selection.index]
        selection.annotation.set_text(
            f"Player: {shot_data['player']}\n"
            f"Minute: {shot_data['minute']}\n"
            f"xG: {shot_data['xG']}\n"
            f"Result: {shot_data['result']}\n"
        )
        selection.annotation.get_bbox_patch().set(fc = "white", alpha = 0.7)



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
pitch = VerticalPitch(pitch_type = "opta", line_zorder = 2, pitch_color = "#f0f0f0", line_color = "black", half = True)

fig, ax = pitch.draw(figsize=(10, 10))
shots_plot(xG_df, ax, pitch)

st.pyplot(fig)





