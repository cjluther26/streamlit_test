from utils.understat_utils import (
    get_understat_matches,
    get_match_ids,
    get_understat_match_data_mutliple,
    create_shots_df_multiple
)

# # Get EPL matches for 2024 season, up to now...
# epl_matches = get_understat_matches(league_id = "EPL", year = 2024)

# # Isolate match IDs
# epl_match_ids = get_match_ids(epl_matches)
epl_match_ids = [26779, 26780]

# Get data for each match
matches_shot_data_list = get_understat_match_data_mutliple(epl_match_ids)

# Create shots DataFrame
shots_df = create_shots_df_multiple(matches_shot_data_list)

# Save dataframe
shots_df.to_csv("EPL_2024_match_shots.csv", index = False)