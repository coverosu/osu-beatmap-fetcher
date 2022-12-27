from pathlib import Path
from typing import Optional, TypedDict

import requests

import common


class BeatmapFromSetIdResult(TypedDict):
    downloaded: bool
    beatmap_path: Optional[Path]


def _beatmap_from_set_id(set_id: int) -> BeatmapFromSetIdResult:
    response = requests.get(
        f"https://api.chimu.moe/v1/download/{set_id}",
        headers={
            "Accept": "application/octet-stream",
        },
    )

    if response.status_code not in range(200, 300):
        return {
            "downloaded": False,
            "beatmap_path": None,
        }

    new_beatmap = common.beatmaps.NEW_MAPS_FOLDER / f"{set_id}.osz"

    new_beatmap.write_bytes(response.content)

    return {
        "downloaded": True,
        "beatmap_path": new_beatmap,
    }


def beatmap_from_set_id(set_id: int) -> Optional[Path]:
    result = _beatmap_from_set_id(set_id)

    if not result["downloaded"]:
        print(f"couldn't download {set_id}.osz")

    return result["beatmap_path"]
