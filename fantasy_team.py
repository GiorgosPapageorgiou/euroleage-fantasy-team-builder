from euroleague_api.standings import Standings
from euroleague_api.boxscore_data import BoxScoreData
import pandas as pd
import math
import numpy as np
import players_data

boxscoredata = BoxScoreData()
season = '2024'
playerstats = boxscoredata.get_player_boxscore_stats_single_season(season)

# Define columns to keep
columns_to_keep = [
    'Player_ID', 'Gamecode', 'Player', 'Team', 'Minutes', 'Points', 'FieldGoalsMade2', 'FieldGoalsAttempted2',
    'FieldGoalsMade3', 'FieldGoalsAttempted3', 'FreeThrowsMade', 'FreeThrowsAttempted', 
    'TotalRebounds', 'Assistances', 'Steals', 'Turnovers', 'BlocksFavour', 
    'BlocksAgainst', 'FoulsCommited', 'FoulsReceived'
]
# Filter DataFrame to keep only specified columns
playerstats = playerstats[columns_to_keep]

# Remove the teams stats from the players stats
playerstats = playerstats[playerstats['Player_ID'] != 'Total']
playerstats = playerstats[playerstats['Player_ID'] != 'Team']

# Sort DataFrame by 'Gamecode' in descending order (highest to lowest)
playerstats = playerstats.sort_values(by='Gamecode', ascending=True)
playerstats.rename(columns={'Gamecode': 'gamenumber'}, inplace=True)


standings = Standings()
gamescore = standings.get_game_metadata_season(season)

# Filter DataFrame to keep only specified columns
gamescore = gamescore[['gamenumber', 'date', 'homecode', 'homescore', 'awaycode', 'awayscore']]

# Sort DataFrame by 'gamenumber' in ascending order (lowest to highest)
gamescore = gamescore.sort_values(by='gamenumber', ascending=True)

# Initialize a new column 'teamwin' based on the score comparison
gamescore['teamwin'] = gamescore.apply(lambda v: v['homecode'] if v['homescore'] > v['awayscore'] else v['awaycode'], axis=1)

# Merge player stats with game results to check if their team won
playerstats = pd.merge(playerstats, gamescore[['gamenumber', 'teamwin']], on='gamenumber', how='left')


# Calculate FP for each player using the new column names
playerstats['FP'] = (
    playerstats['Points'] +
    playerstats['TotalRebounds'] +
    playerstats['Assistances'] +
    playerstats['Steals'] +
    playerstats['BlocksFavour'] +
    playerstats['FoulsReceived'] -
    playerstats['Turnovers'] -
    playerstats['BlocksAgainst'] -
    playerstats['FoulsCommited'] -
    ((playerstats['FieldGoalsAttempted2'] + playerstats['FieldGoalsAttempted3']) - 
     (playerstats['FieldGoalsMade2'] + playerstats['FieldGoalsMade3'])) -
    (playerstats['FreeThrowsAttempted'] - playerstats['FreeThrowsMade'])
)

# Adjust FP for players on winning teams 
# Update the 'FP' based on the winning condition
playerstats['FP'] = playerstats.apply(lambda row: (row['FP'] + 0.1*
abs(row['FP'])) if row['teamwin'] == row['Team'] else row['FP'], axis=1)

# Apply lambda function to set FP to None if Minutes equals 'DNP' - Did Not Play
playerstats['FP'] = playerstats.apply(lambda row: None if row['Minutes'] == 'DNP' else row['FP'], axis=1)

# Round to 2 decimal places
playerstats['FP'] = round(playerstats['FP'], 2)

# Sort the DataFrame first by 'Player_ID' and then by 'Gamecode'
playerstats = playerstats.sort_values(by=['Player_ID', 'gamenumber']).reset_index(drop=True)

# Create a Dict with players as key and a list of his Fantasy Points as value 
players_FP = {}
for index, row in playerstats.iterrows():
    player = row['Player']
    fp = row['FP']
    if player not in players_FP : 
        players_FP[player] = []
        players_FP[player].append(fp)
    else :
        players_FP[player].append(fp)

for player, FPs in players_FP.items() :
    average = np.nanmean(FPs)  # Automatically ignores NaN values
    rounded_average_fp = round(average, 2)  # Round to 2 decimal places
    players_FP[player] = {'FP': FPs, 'average_FP': rounded_average_fp}  # Add as a new attribute

# Sorting the dictionary by key
players_FP = dict(sorted(players_FP.items()))
    
for player, FPs in players_FP.items() :
    #print(f"'{player}': {{'FP': {FPs['FP']}, 'average_FP': {FPs['average_FP']}, 'position': ' ', 'cost': 0 }} ,")
    players_data.data[player]['FP'] = FPs['FP']

for player, FPs in players_data.cleaned_data.items() :
    print(f"'{player}': {{'FP': {FPs['FP']}, 'average_FP': {FPs['average_FP']}, 'position': '{FPs['position']}', 'cost': {FPs['cost']} }} ,")