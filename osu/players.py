import time
from typing import Optional, TypedDict

import ossapi
from ossapi.enums import ScoreType

import common
from objects.player import Player


class CreatePlayerFromUserNameResult(TypedDict):
    success: bool
    player: Optional[Player]


def _create_player_from_user_name(
    user_name: str,
    osu_api_v1_client: ossapi.Ossapi,
) -> CreatePlayerFromUserNameResult:
    user = osu_api_v1_client.get_user(
        user=user_name,
        user_type="string",
    )

    if not user:
        return {
            "success": False,
            "player": None,
        }

    assert user.username and user.user_id
    player = Player(
        user_name=user.username,
        id=user.user_id,
        most_recent_scores=None,
    )

    return {
        "success": True,
        "player": player,
    }


def create_player_from_user_name(user_name: str) -> Optional[Player]:
    results = _create_player_from_user_name(
        user_name=user_name,
        osu_api_v1_client=common.osu_api.v1,
    )

    if not results["success"]:
        print(f"{user_name} doesn't exist.")
        return None

    return results["player"]


class CreatePlayersFromUserNamesResult(TypedDict):
    success: bool
    message: Optional[str]
    players: list[Player]


def _create_players_from_user_names(
    user_names: list[str],
    osu_api_v1_client: ossapi.Ossapi,
) -> CreatePlayersFromUserNamesResult:
    players: list[Player] = []
    message: str = ""

    for player_name in user_names:
        results = _create_player_from_user_name(
            user_name=player_name,
            osu_api_v1_client=osu_api_v1_client,
        )

        if not results["success"]:
            message += f"{player_name} doesn't exist\n"
            continue

        player = results["player"]
        assert player, f"{player_name} does not exist"
        players.append(player)

        time.sleep(0.5)

    return {
        "success": True,
        "message": message or None,
        "players": players,
    }


def create_players_from_user_names(user_names: list[str]) -> list[Player]:
    results = _create_players_from_user_names(
        user_names=user_names,
        osu_api_v1_client=common.osu_api.v1,
    )

    if results["message"] is not None:
        print(results["message"])

    return results["players"]


class UpdatePlayersRecentResult(TypedDict):
    success: bool
    updated_players: Optional[list[Player]]


def _update_players_recent(
    players: list[Player],
    osu_api_v2_client: ossapi.OssapiV2,
) -> UpdatePlayersRecentResult:
    for player in players:
        time.sleep(0.5)
        recent_scores = osu_api_v2_client.user_scores(
            user_id=player.id,
            type_=ScoreType.RECENT,
            include_fails=True,
        )

        if not recent_scores:
            player.most_recent_scores = None
            continue

        player.most_recent_scores = recent_scores

    return {"success": True, "updated_players": players}


def update_players_recent(players: list[Player]) -> list[Player]:
    results = _update_players_recent(
        players=players,
        osu_api_v2_client=common.osu_api.v2,
    )

    assert results["success"], "TODO: handle this error"
    assert results["updated_players"], "TODO: handle this error"

    return results["updated_players"]
