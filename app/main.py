from fastapi import FastAPI
import json
import featuretools as ft
import pandas as pd
import numpy as np
from woodwork.logical_types import Categorical
import uvicorn
import warnings
import logging
import os


# suppress warnings
warnings.filterwarnings("ignore")

# import json file with data
# with open('app/data.json', 'r') as json_file: # when not running docker MAYBE USELESS
with open('data.json', 'r') as json_file:  # when running docker
    data = json.load(json_file)

# prepare first dataframe from json file
players = [{'player_ID': item['player_ID']} for item in data['data']]
players_df = pd.DataFrame(players)

# prepare second dataframe from json file
quests_info = []
for item in data['data']:
    for quest in item['quests']:
        quests_info.append(quest)
quests_df = pd.DataFrame(quests_info)

# missing ID in second dataframe, so give one to avoid errors
quests_df['quest_ID'] = np.arange(1, len(quests_df) + 1)

# use featuretools for automated feature extraction from the 2 Dataframes according to manual of library
es = ft.EntitySet(id="player_data")

es = es.add_dataframe(
    dataframe_name="players",
    dataframe=players_df,
    index="player_ID",
)

es = es.add_dataframe(
    dataframe_name="quests",
    dataframe=quests_df,
    index="quest_ID",
    # time_index="quest_date", #FIX IT
    logical_types={  # be careful with type of data
        "quest_status": Categorical,
        "duration": Categorical,
    },
)

es = es.add_relationship("players", "player_ID", "quests", "player_ID")

feature_matrix, feature_defs = ft.dfs(entityset=es, target_dataframe_name="players")

# keep only interesting features after inspection since:
# 1. Everything that is about player_experience no extra info
# 2. Useless features such as the most freq occurring value of the day, the number of unique elements in the day, etc.
feature_matrix_final = feature_matrix[['COUNT(quests)', 'MEAN(quests.quest_experience)', 'SUM(quests.quest_experience)',
                                       'MAX(quests.quest_experience)', 'MIN(quests.quest_experience)',
                                       'SKEW(quests.quest_experience)', 'STD(quests.quest_experience)',
                                       'MEAN(quests.difficulty_level)', 'SUM(quests.difficulty_level)',
                                       'MAX(quests.difficulty_level)', 'MIN(quests.difficulty_level)',
                                       'SKEW(quests.difficulty_level)', 'STD(quests.difficulty_level)',
                                       'MODE(quests.quest_status)', 'NUM_UNIQUE(quests.quest_status)',
                                       'MODE(quests.duration)', 'NUM_UNIQUE(quests.duration)']]

# handle missing values but firstly be careful with categorical data
feature_matrix_final['MODE(quests.duration)'] = (feature_matrix_final['MODE(quests.duration)'].
                                                 cat.add_categories("missing"))
feature_matrix_final['MODE(quests.quest_status)'] = (feature_matrix_final['MODE(quests.quest_status)'].
                                                     cat.add_categories("missing"))
feature_matrix_final = feature_matrix_final.fillna("missing")


# Create a logger
logger = logging.getLogger("fastAPI_app")
# Define the log file path
log_file = "/app/logs/app.log"
# Ensure the log directory exists
os.makedirs(os.path.dirname(log_file), exist_ok=True)
# Configure the logger to write to the log file
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# it's time for the API
app = FastAPI()


# define root
@app.get("/")
async def root():
    return {"status": "UP"}


# define the route handler for raw data
@app.get("/get_raw_data/{player_id}")
async def get_info(player_id: str):
    try:
        for item in data['data']:
            if item['player_ID'] == player_id:
                return_raw = {player_id: item['quests']}
                logger.info("Getting raw data of player successfully.")
                return return_raw
        logger.error("Player ID was wrong for getting raw data.")
        return {"error": "Player not found"}
    except Exception as e:
        logger.error(f"Error in getting raw data: {str(e)}")
        return {"error": "An error occurred while getting raw data."}


# define the route handler for features extracted
@app.get("/get_features/{player_id}")
async def get_infooo(player_id: int):
    try:
        return_features = {player_id: feature_matrix_final.loc[player_id].to_dict()}
        logger.info("Getting features of player successfully.")
        return return_features
    except Exception as e:
        logger.error(f"Error in getting features: {str(e)}")
        return {"error": "An error occurred while getting features."}


# run the FastAPI app with Uvicorn in the following host, port when not running docker
if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000)
