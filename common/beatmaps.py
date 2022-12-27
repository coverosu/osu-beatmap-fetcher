from pathlib import Path

import config

SONGS_FOLDER = Path(config.osu_beatmap_path)

NEW_MAPS_FOLDER = Path("./beatmaps")

downloaded: list[int] = []
