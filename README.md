# osu! beatmap fetcher

<sup><sub>this is still a work in progress, i kind of rushed through it cause i wanted maps lol (12/26/22)</sub></sup>

## Description
This python project is a project that downloads beatmaps from osu! by watching the recent scores of a list of specified players. If you don't have the maps they are playing, they are downloaded and stored in a local folder called `beatmaps`.

## Configuration 

To use this project, you will need to obtain an API key from the osu! API website (https://osu.ppy.sh/wiki/en/osu%21api). You will also need to obtain client credentials from the osu! API website in order to use the V2 API.

You will need to update the `osu_api_key`, `client_id`, and `client_secret` variables in the `config.py` file with your own API key and client credentials.

You will also need to update the `osu_beatmap_path` variable in the `config.py` file with the path to your osu! songs folder.

## Installation

1. Clone this repository
2. Navigate to the root directory of the repository
3. Install the required packages: `pip install -r requirements.txt`

## Running the project
1. Navigate to the root directory of the repository
2. Run the `main.py` script: `python main.py`