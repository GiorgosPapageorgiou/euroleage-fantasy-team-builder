from euroleague_api.standings import Standings
from euroleague_api.boxscore_data import BoxScoreData
import pandas as pd


boxscoredata = BoxScoreData()
season = '2024'
playerstats = boxscoredata.get_player_boxscore_stats_single_season(season)

# Define columns to keep
columns_to_keep = [
    'Gamecode', 'Player_ID', 'Player', 'Team', 'Minutes', 'Points', 'FieldGoalsMade2', 'FieldGoalsAttempted2',
    'FieldGoalsMade3', 'FieldGoalsAttempted3', 'FreeThrowsMade', 'FreeThrowsAttempted', 
    'TotalRebounds', 'Assistances', 'Steals', 'Turnovers', 'BlocksFavour', 
    'BlocksAgainst', 'FoulsCommited', 'FoulsReceived'
]

# Filter DataFrame to keep only specified columns
playerstats = playerstats[columns_to_keep]

# Remove the teams stats from the players stats
playerstats = playerstats[playerstats['Player_ID'] != 'Total']

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
playerstats['FP'] = playerstats.apply(lambda row: row['FP'] * 1.1 if row['teamwin'] == 'Team' else row['FP'], axis=1)


# Print each row
for index, row in playerstats.iterrows():
    print(f"Row {index}: {row.to_dict()}")  # Print row as a dictionary for readability
print(gamescore)

