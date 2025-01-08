import pandas as pd
import numpy as np
import streamlit as st
from mplsoccer import VerticalPitch, Pitch
import mplcursors




# Load data
test_df = pd.read_csv("./EPL_2024_match_shots.csv")

# Clean data
test_df.rename(columns={"X": "x", "Y": "y"}, inplace=True)
test_df["xG"] = test_df["xG"].fillna(0)
test_df["team"] = np.where(test_df["h_a"] == "h", test_df["h_team"], test_df["a_team"])
test_df["date_str"] = test_df["date"].str.slice(0,10)
test_df["match_name"] = "(" + test_df["date_str"] + ") " + test_df["h_team"] + " vs. " + test_df["a_team"]

test_df = test_df[["date_str", "match_name", "id", "minute", "result", "x", "y", "xG", "player", "team", "situation", "shotType", "match_id", "h_goals", "a_goals", "player_assisted", "lastAction", "h_team", "a_team"]]
test_df = test_df.sort_values(by=["date_str", "match_name", "team", "player", "minute"])


def isolate_match_df(df: pd.DataFrame, match_name: str) -> pd.DataFrame:
    """
    Isolates a DataFrame to a specific match
    
    Parameters:
    - df (pd.DataFrame): the DataFrame to filter
    - match_name (str): the match to filter by

    Returns:
    - pd.DataFrame: the filtered DataFrame

    """
    # Filter to match
    match_df = df[df["match_name"] == match_name]

    return match_df



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

    # Filter to team (if selected)
    if team: 

        df = df[df["team"] == team] 

    # Filter to player (if selected)
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
            x = 100 * x["x"],
            y = 100 * x["y"],
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

    # Isolate home and away teams
    labels["home_team"] = df["h_team"].iloc[0]
    labels["away_team"] = df["a_team"].iloc[0]

    # Isolate date (crudely)
    labels["date_str"] = df["date_str"].iloc[0]

    # Isolate final score (crudely)
    labels["home_goals_total"] = df["h_goals"].iloc[0]
    labels["away_goals_total"] = df["a_goals"].iloc[0]

    return labels


# match_name = "(2024-08-16) Manchester United vs. Fulham"
# match_df = isolate_match_df(test_df, match_name)
# labels = get_plot_labels(match_df)
# print(labels)


#######################
#### STREAMLIT APP ####
#######################

# Ensure there is actually data available
if test_df.empty:
    st.error("No data available to display.")
    st.stop()

# Configure streamlit app
match_names = test_df["match_name"].unique()
match_name = st.selectbox(
    label = "Select a match",
    options = match_names,
    index = 0
)

# Isolate match data
match_df = isolate_match_df(test_df, match_name)



# st.title(f"Tottenham vs. Nottingham Forest (2024-12-26)")

# Get labels
labels = get_plot_labels(match_df)

# Set titles
st.title(f"{labels["home_team"]} vs. {labels["away_team"]} ({labels["date_str"]})")
st.subheader(f"Final Score: {labels["home_goals_total"]} - {labels["away_goals_total"]}")
st.subheader("Filter to a team/player to see all of their shots in the game!")


# Configure team selection
team = st.selectbox(
    label = "Select a team",
    options = match_df["team"].unique(),
    index = 0
)

# Isolate players to plot, add empty string to allow for all players, and sort
available_players = match_df[match_df["team"] == team]["player"].unique().tolist()
available_players.append("")
available_players.sort()

# Configure player selection
player = st.selectbox(
    label = "Select a player",
    options = available_players,
    index = 0
)

# Isolate data
xG_df = filter_data(match_df, team = team, player = player)

# Create a pitch
pitch = Pitch(pitch_type = "opta", line_zorder = 2, pitch_color = "#f0f0f0", line_color = "black", half = True)

fig, ax = pitch.draw(figsize=(10, 10))
shots_plot(xG_df, ax, pitch)

st.pyplot(fig)

