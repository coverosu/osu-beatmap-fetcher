"""osu! beatmap fetcher: downloads beatmaps from watching your favorite players"""
import asyncio
from pathlib import Path
from typing import Optional

import aiohttp
import requests
from ossapi import Score
from ossapi.enums import ScoreType

import common
import config
from objects.player import Player


def init_downloaded_beatmaps() -> None:
    for beatmap in common.beatmaps.SONGS_FOLDER.iterdir():
        if beatmap.is_file():
            continue

        try:
            beatmap_set_id, *etc = beatmap.name.split(" ")
        except:
            continue

        common.beatmaps.downloaded.append(int(beatmap_set_id))


def init_common() -> None:
    init_downloaded_beatmaps()
    common.http.SESSION = aiohttp.ClientSession()


async def get_player_user_id(user_name: str) -> Optional[int]:
    user = common.osu_api.v1.get_user(
        user=user_name,
        user_type="string",
    )

    if not user:
        return None

    return user.user_id


async def get_recent_scores(user_id: int) -> Optional[list[Score]]:
    try:
        scores = common.osu_api.v2.user_scores(
            user_id=user_id,
            type_=ScoreType.RECENT,
            include_fails=True,
        )
    except requests.exceptions.JSONDecodeError:
        return None

    if not scores:
        return None

    return scores


async def get_player_with_updated_recent_scores(user_name: str) -> Optional[Player]:
    # check database first
    user_id = common.database.get(user_name)

    if user_id is None:
        user_id = await get_player_user_id(user_name)
        if user_id is None:
            print("Could not retrieve user's id.")
            return None

    common.database.set(user_name, user_id)

    assert isinstance(user_id, int)

    recent_scores = await get_recent_scores(user_id)

    if recent_scores is None:
        print(f"no recent scores found for {user_name}")
    else:
        print(f"recent scores found for {user_name}")

    return Player(
        user_name=user_name,
        id=user_id,
        most_recent_scores=recent_scores,
    )


async def get_players_with_updated_recent_scores(
    user_names: list[str],
) -> list[Player]:
    tasks = [
        get_player_with_updated_recent_scores(user_name) for user_name in user_names
    ]
    players: list[Optional[Player]] = await asyncio.gather(*tasks)

    real_players = [player for player in players if player]

    return real_players


async def download_set_from_set_id(set_id: int, beatmap_title: str) -> Optional[Path]:
    try:
        response = await common.http.SESSION.get(
            f"https://api.chimu.moe/v1/download/{set_id}",
            headers={
                "Accept": "application/octet-stream",
            },
        )
    except aiohttp.ClientConnectionError as e:
        print("error when downloading map:", e)
        return None

    if response.status not in range(200, 300):
        print(f"Couldn't download {set_id}.osz / {beatmap_title}")
        return None

    new_beatmap = common.beatmaps.NEW_MAPS_FOLDER / f"{set_id}.osz"

    new_beatmap.write_bytes(await response.content.read())

    common.beatmaps.downloaded.append(set_id)

    return new_beatmap


async def download_set_from_player_recent(player: Player) -> Optional[list[Path]]:
    tasks = []

    if not player.most_recent_scores:
        print(f"{player.user_name} doesn't have any recent scores")
        return None

    for score in player.most_recent_scores:
        if not score.beatmapset:
            print(f"can't get beatmap from {player.user_name}")
            continue

        set_id = score.beatmapset.id
        title = score.beatmapset.title

        if set_id in common.beatmaps.downloaded:
            print("you already have", title)
            continue

        new_map = common.beatmaps.NEW_MAPS_FOLDER / f"{set_id}.osz"
        if new_map.exists():
            print("its already in the `beatmaps` folder:", title)
            continue

        print(f"downloading {set_id} from {player.user_name}")

        tasks.append(download_set_from_set_id(set_id, title))

    new_maps_path: list[Optional[Path]] = await asyncio.gather(*tasks)

    valid_new_maps = [bmap for bmap in new_maps_path if bmap]

    return valid_new_maps


async def download_sets_from_players_recent(players: list[Player]) -> None:
    tasks = [download_set_from_player_recent(player) for player in players]

    map_paths: list[Optional[list[Path]]] = await asyncio.gather(*tasks)

    downloaded_sets = [bmap for bmap in map_paths if bmap]

    all_maps_downloaded = []
    for set in downloaded_sets:
        all_maps_downloaded.extend(set)

    print(f"successfully downloaded {len(downloaded_sets)} sets from players!")
    print(f"successfully downloaded {len(all_maps_downloaded)} maps from players!")

    return None


async def clean_up() -> None:
    print("Cleaning program for shutdown...")
    common.database.update_database_file()
    await common.http.SESSION.close()
    print("finished shutting down.")


async def main() -> int:

    init_downloaded_beatmaps()
    init_common()

    iterations = 0

    try:
        while True:
            players = await get_players_with_updated_recent_scores(
                config.osu_users_to_spectate,
            )

            assert players, "no players found to spectate"

            await download_sets_from_players_recent(players)

            len_players = len(players)
            for idx in range(len_players * 2):
                print(f"rate limit waiting {idx+1}/{len_players * 2} seconds")
                await asyncio.sleep(1)

            iterations += 1
            print(f"passed through {iterations} iterations!")
    except KeyboardInterrupt:
        await clean_up()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
