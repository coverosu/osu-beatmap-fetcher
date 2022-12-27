"""osu! beatmap fetcher: downloads beatmaps from watching your favorite players"""
import time

import common
import config
import osu


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

    if not common.beatmaps.NEW_MAPS_FOLDER.exists():
        common.beatmaps.NEW_MAPS_FOLDER.mkdir(exist_ok=True)

    common.players = osu.players.create_players_from_user_names(
        user_names=config.osu_users_to_spectate,
    )

    osu.players.update_players_recent(
        players=common.players,
    )


def main() -> int:
    print("initializing players...")
    init_common()
    print("finished initialization")
    LEN_PLAYERS = len(common.players)

    iterations = 0

    while True:
        for player in common.players:
            if player.most_recent_scores is None:
                print(f"{player.user_name} has no recent scores")
                continue

            for score in player.most_recent_scores:
                if not score.beatmapset:
                    print(f"no beatmap set was found for", player.user_name)
                    continue

                beatmap_set = score.beatmapset

                if beatmap_set.id in common.beatmaps.downloaded:
                    print("you already have", beatmap_set.title)
                    continue

                new_map = common.beatmaps.NEW_MAPS_FOLDER / f"{beatmap_set.id}.osz"
                if new_map.exists():
                    print("its already in the `beatmaps` folder:", beatmap_set.title)
                    continue

                print(f"downloading {beatmap_set.id} from {player.user_name}")
                beatmap = osu.download.beatmap_from_set_id(beatmap_set.id)

                if beatmap is None:
                    print(f"Can't download beatmap from", player.user_name)
                    continue

                common.beatmaps.downloaded.append(beatmap_set.id)

                print(
                    f"Successfully downloaded beatmap ({beatmap.name} / {beatmap_set.title}) from {player.user_name}"
                )

                time.sleep(2)

        iterations += 1

        print(f"finished iterating for the {iterations} time!")

        for idx in range(LEN_PLAYERS * 2):
            print(f"rate limit waiting {idx}/{LEN_PLAYERS * 2}")
            time.sleep(1)

        common.players = osu.players.update_players_recent(
            players=common.players,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
