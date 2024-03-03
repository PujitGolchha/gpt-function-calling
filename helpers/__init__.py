import pickle 
import os
from dotenv import dotenv_values
from pathlib import Path

#setting the different credentials
path = Path(__file__).parent.absolute()
config = dotenv_values(str(path)+"/keys.env")
OPENAI_API_KEY = config["OPEN_AI_KEY"]

spotify_client_id = config["spotify_client_id"]
spotify_client_secret = config["spotify_client_secret"]

music_brainz_app=config["music_brainz_app"]
music_brainz_version=config["music_brainz_version"]
music_brainz_contact=config["music_brainz_contact"]

open_street_maps_user_agent= config["open_street_maps_user_agent"]

os.chdir("..")
print('Working directory while importing helpers updated to:', os.getcwd())

def upload_file(path, data):
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def download_file(path):
    with open(path, 'rb') as f:
        loaded_dict = pickle.load(f)
    return loaded_dict