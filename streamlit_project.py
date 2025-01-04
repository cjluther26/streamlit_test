# import pandas as pd
# import numpy as np
# import streamlit as st
# from mplsoccer import VerticalPitch
# import mplcursors


# st.title("Tottenham vs. Nottingham Forest (2024-12-26)")
# st.subheader("Filter to a team/player to see all of their shots in the game!")

# # Load data
# test_df = pd.read_csv("./test_data_shots.csv")

# # Clean data
# test_df['xG'] = test_df['xG'].fillna(0)
# test_df['team'] = np.where(test_df["h_a"] == "h", test_df["h_team"], test_df["a_team"])
# test_df = test_df[["id", "minute", "result", "X", "Y", "xG", "player", "team", "situation", "shotType", "match_id", "h_goals", "a_goals", "player_assisted", "lastAction", "date"]]
# test_df = test_df.sort_values(by=['team', 'player'])


# # Ensure there is actually data available
# if test_df.empty:
#     st.error("No data available to display.")
#     st.stop()


# def filter_data(df: pd.DataFrame, team: str, player: str):
#     """
#     """

#     if team: 

#         df = df[df["team"] == team] 

#     if player and player != "": 

#         df = df[df["player"] == player] 
    
#     return df

# def shots_plot(df: pd.DataFrame, ax, pitch):
#     """
#     """

#     ax.set_title("xG Plot")
#     scatter = []

#     # Iterate through each record
#     for x in df.to_dict(orient = "records"):

#         shot = pitch.scatter(
#             x = 100 * x["X"],
#             y = 100 * x["Y"],
#             ax = ax,
#             s = 1000 * x["xG"],
#             color = "green" if x["result"] == "Goal" else "white",
#             edgecolors = "black",
#             alpha = 1 if x["result"] == "Goal" else 0.5,
#             zorder = 2 if x["result"] == "Goal" else 1
#         )

#         # Append to scatter (list of points)
#         scatter.append(shot)

#     # Enable interactive tooltips
#     cursor = mplcursors.cursor(
#         scatter,
#         hover = True
#     )
    
#     @cursor.connect("add")
#     def on_add(selection):
#         """
#         """
#         shot_data = df.iloc[selection.index]
#         selection.annotation.set_text(
#             f"Player: {shot_data['player']}\n"
#             f"Minute: {shot_data['minute']}\n"
#             f"xG: {shot_data['xG']}\n"
#             f"Result: {shot_data['result']}\n"
#         )
#         selection.annotation.get_bbox_patch().set(fc = "white", alpha = 0.7)



# # Configure streamlit app
# teams = test_df["team"].unique()

# team = st.selectbox(
#     label = "Select a team",
#     options = test_df["team"].unique(),
#     index = 0
# )

# # Isolate players to plot, add empty string to allow for all players, and sort
# available_players = test_df[test_df["team"] == team]["player"].unique().tolist()
# available_players.append("")
# available_players.sort()

# player = st.selectbox(
#     label = "Select a player",
#     options = available_players,
#     index = 0
# )

# # Isolate data
# xG_df = filter_data(test_df, team = team, player = player)


# # Create a pitch
# pitch = VerticalPitch(pitch_type = "opta", line_zorder = 2, pitch_color = "#f0f0f0", line_color = "black", half = True)

# fig, ax = pitch.draw(figsize=(10, 10))
# shots_plot(xG_df, ax, pitch)

# st.pyplot(fig)





import pandas as pd
import numpy as np
import streamlit as st
from mplsoccer import VerticalPitch
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from io import BytesIO

st.title("Tottenham vs. Nottingham Forest (2024-12-26)")
st.subheader("Filter to a team/player to see all of their shots in the game!")

# Load data
test_df = pd.read_csv("./test_data_shots.csv")

# Clean data
test_df['xG'] = test_df['xG'].fillna(0)
test_df['team'] = np.where(test_df["h_a"] == "h", test_df["h_team"], test_df["a_team"])
test_df = test_df[["id", "minute", "result", "X", "Y", "xG", "player", "team", "situation", "shotType", "match_id", "h_goals", "a_goals", "player_assisted", "lastAction", "date"]]
test_df = test_df.sort_values(by=['team', 'player'])

if test_df.empty:
    st.error("No data available to display.")
    st.stop()

# Filter function
def filter_data(df: pd.DataFrame, team: str, player: str):
    if team:
        df = df[df["team"] == team]
    if player and player != "":
        df = df[df["player"] == player]
    return df

# Configure Streamlit app
teams = test_df["team"].unique()

team = st.selectbox(
    label="Select a team",
    options=teams,
    index=0
)

available_players = test_df[test_df["team"] == team]["player"].unique().tolist()
available_players.append("")
available_players.sort()

player = st.selectbox(
    label="Select a player",
    options=available_players,
    index=0
)

# Filter data
xG_df = filter_data(test_df, team=team, player=player)

# Create the pitch using mplsoccer
pitch = VerticalPitch(
    pitch_type='opta', 
    pitch_color='white', 
    line_color='black', 
    line_zorder=2, 
    half=True
)

fig, ax = pitch.draw(figsize=(10, 6))

# Save the pitch as an image in memory
buffer = BytesIO()
plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
plt.close(fig)
buffer.seek(0)

# Create Plotly scatter plot
fig = go.Figure()

# Add the pitch as a background image
fig.add_layout_image(
    dict(
        source="data:image/png;base64," + buffer.read().decode('latin1'),
        xref="x",
        yref="y",
        x=0,
        y=100,
        sizex=100,
        sizey=100,
        xanchor="left",
        yanchor="bottom",
        layer="below"
    )
)

# Add scatter points for shots
for _, shot in xG_df.iterrows():
    fig.add_trace(go.Scatter(
        x=[100 * shot["X"]],
        y=[100 * shot["Y"]],
        mode='markers',
        marker=dict(
            size=10 + (50 * shot['xG']),  # Scale marker size by xG
            color='green' if shot['result'] == 'Goal' else 'red',
            opacity=0.7,
            line=dict(color='black', width=1)
        ),
        hovertemplate=(
            f"Player: {shot['player']}<br>"
            f"Minute: {shot['minute']}<br>"
            f"xG: {shot['xG']}<br>"
            f"Result: {shot['result']}<extra></extra>"
        ),
        name=f"Shot by {shot['player']}"
    ))

# Update plot layout
fig.update_layout(
    xaxis=dict(range=[0, 100], showgrid=False, zeroline=False),
    yaxis=dict(range=[0, 100], showgrid=False, zeroline=False),
    width=800,
    height=600,
    plot_bgcolor='white',
    xaxis_title="Pitch X",
    yaxis_title="Pitch Y",
    title="Shot Map with xG",
    title_x=0.5
)

# Flip Y-axis to align with soccer pitch orientation
fig.update_yaxes(autorange="reversed")

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)
