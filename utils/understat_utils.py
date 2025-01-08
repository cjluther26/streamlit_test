import requests 
from bs4 import BeautifulSoup
import json 
import pandas as pd
from typing import Dict, List, Any
import logging



def clean_understat_return(understat_return: str):
    """
    Cleans a string derived from a bs4.element.Tag type, obtained from Understat, and converts into a JSON

    Parameters:
    - understat_return (str): string object encased within a bs4 element Tag from Understat

    Returns:
    - json_data (Dict): JSON object containing the data
    
    """

    # Isolate string
    understat_string = understat_return.string

    # Define starting/stopping positions
    ind_start = understat_string.index("('") + 2
    ind_end = understat_string.index("')")

    # Isolate everything between
    json_data_string_raw = understat_string[ind_start:ind_end]

    # Encode/decode to clean
    json_data_string = json_data_string_raw.encode("utf8").decode("unicode_escape")

    # Convert from string to JSON
    json_data = json.loads(json_data_string)

    return json_data




    


def get_understat_matches(league_id: str = "EPL", year: int = 2024) -> str:
    """
    Get matches for a given league in a given year from Understat

    Parameters:
    - league_id (str): name of the league (i.e. EPL, Bundesliga, etc.)
    - year (int): year (i.e. 2024, 2023, etc.)

    Returns: 
    - matches_json (Dict): dictionary containing data on matches

    """

    # Declare GET parameters
    url = f"https://understat.com/league/{league_id}/{year}"

    logging.info(
        f"Getting match data for matches in the {league_id} in {year}..."
    )

    # GET request
    response = requests.get(url)

    # Isolate content
    team_soup = BeautifulSoup(response.content, 'lxml')
    scripts = team_soup.find_all('script')
    data_string = scripts[1].string

    # Convert to JSON
    matches_json = clean_understat_return(data_string)

    # Convert to JSON
    all_matches_json = clean_understat_return(data_string)

    # Remove any matches without results
    matches_json = [obs for obs in all_matches_json if obs["isResult"] is True]

    return matches_json

    


def get_match_ids(matches_json: Dict) -> List:
    """
    Generates a list of match IDs for a given league-year combination

    Parameters:
    - matches_json (Dict): matches for a given league-year

    Returns:
    - match_ids (List): list of match IDs

    """

    # Isolate match IDs
    match_ids = [match["id"] for match in matches_json]

    return match_ids




def get_understat_match_data(match_id: str = "26779") -> Dict:
    """
    Get data for a given match ID from Understat

    Parameters:
    - match_id (str): match ID in Understat

    Returns: 
    - match_data_json (Dict): dictionary containing data on the match

    """

    if match_id is not int:

        try: 

            match_id = int(match_id)

        except ValueError:
            
            raise ValueError("Match ID must be an integer")

    logging.info(
        f"Getting data for match ID {match_id}"
    )

    # Declare GET parameters
    url = f"https://understat.com/match/{match_id}"

    # GET request
    response = requests.get(url)

    # Isolate content
    team_soup = BeautifulSoup(response.content, 'lxml')
    scripts = team_soup.find_all('script')
    data_string = scripts[1].string

    # Convert to JSON
    match_data_json = clean_understat_return(data_string)

    return match_data_json



def get_understat_match_data_mutliple(match_ids: List) -> List[Dict[Any, Any]]:
    """
    Get data for a list of match IDs from Understat

    Parameters:
    - match_ids (str): match ID in Understat

    Returns: 
    - matches_shot_data_list (List): list of dictionaries, where each dictionary contains data on a given match

    """

    matches_shot_data_list = [get_understat_match_data(x) for x in match_ids]

    return matches_shot_data_list

    




def create_shots_df(shots_json: Dict[Any, Any]) -> pd.DataFrame: 
    """
    Creates a DataFrame of shots for a given match

    Parameters:
    - shots_json (Dict): JSON containing shots for a given match, formatted as  `data = {'h': [...], 'a': [...]}`

    Returns:
    - shots_df (pd.DataFrame): DataFrame containing all shots for a given match
    
    """

    # Create DataFrame for home team's shots
    home_df = pd.DataFrame.from_dict(shots_json["h"])

    # Create DataFrame for away team's shots
    away_df = pd.DataFrame.from_dict(shots_json["a"])

    # Combine!
    shots_df = pd.concat([home_df, away_df], axis = 0, ignore_index = True)

    return shots_df



def create_shots_df_multiple(matches_shot_data_list: List[Dict[Any, Any]]) -> pd.DataFrame: 
    """
    Creates a DataFrame of shots for multiple matches

    Parameters:
    - shots_json_list (List): list of JSONs containing shots for a given match, formatted as  `data = {'h': [...], 'a': [...]}`

    Returns:
    - match_shots_df (pd.DataFrame): DataFrame containing all shots for a given match
    
    """

    # Create list of DataFrames for each match's shots
    list_dfs = list(map(create_shots_df, matches_shot_data_list))

    # Flatten
    match_shots_df = pd.concat(list_dfs)

    return match_shots_df