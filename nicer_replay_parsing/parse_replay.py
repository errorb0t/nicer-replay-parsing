import hashlib
from heroprotocol.versions import protocol96370
import mpyq

from .model import (
    DraftAction,
    DraftActionType,
    Player,
    Replay,
    Team,
    Version,
)
from .util import *


def parse_replay(filename):
    archive = mpyq.MPQArchive(filename)
    contents = archive.header["user_data_header"]["content"]
    header = protocol96370.decode_replay_header(contents)
    version = Version(
        header["m_version"]["m_baseBuild"],
        header["m_version"]["m_major"],
        header["m_version"]["m_minor"],
        header["m_version"]["m_revision"],
        header["m_version"]["m_build"],
        header["m_version"]["m_flags"],
    )

    protocol = import_heroprotocol(version.base_build)
    if protocol is None:
        archive.file.close()
        raise Exception("Unsupported Build")

    # Battlelobby (for battletags)
    battlelobby = archive.read_file("replay.server.battlelobby")

    # Details
    details = protocol.decode_replay_details(archive.read_file("replay.details"))
    date = get_date(details["m_timeUTC"])

    players: dict[str, dict] = {}
    wss_to_player = {}

    for player in details["m_playerList"]:
        toon_handle = f"{player['m_toon']['m_region']}-{player['m_toon']['m_programId'].decode()}-{player['m_toon']["m_realm"]}-{player['m_toon']["m_id"]}"
        if toon_handle == "0-\x00\x00\x00\x00-0-0":
            raise NotImplementedError("Computer Player Found")
        players[toon_handle] = {}
        players[toon_handle]["team"] = Team.RIGHT if player["m_teamId"] else Team.LEFT
        players[toon_handle]["name"] = player["m_name"]
        localized_name = player["m_hero"].decode()
        try:
            hero = get_hero_from_localized(localized_name)
        except KeyError:
            hero = get_hero_from_localized(localized_name.lower())
        players[toon_handle]["hero"] = hero
        players[toon_handle]["battletag"] = get_battletag(battlelobby, player["m_name"])
        wss_to_player[player["m_workingSetSlotId"]] = toon_handle

    # Initdata
    initdata = protocol.decode_replay_initdata(archive.read_file("replay.initData"))
    gamemode = get_gamemode(
        initdata["m_syncLobbyState"]["m_gameDescription"]["m_gameOptions"]["m_ammId"]
    )

    random_value = initdata["m_syncLobbyState"]["m_gameDescription"]["m_randomValue"]
    id_string = "".join(
        sorted([str(player["m_toon"]["m_id"]) for player in details["m_playerList"]])
    )
    replay_id = hashlib.md5((id_string + str(random_value)).encode()).hexdigest()

    # Trackerevents
    duration = None
    battleground = get_battleground_from_localized(details["m_title"].decode())
    tracker_ids_to_player: dict[int, str | None] = {}
    core_ids = []
    draft: list[DraftAction] = []
    firstpick = None
    incomplete = True
    for event in protocol.decode_replay_tracker_events(
        archive.read_file("replay.tracker.events")
    ):
        # Tracker IDs
        if event["_eventid"] == 10 and event["m_eventName"].decode() == "PlayerInit":
            controller = event["m_stringData"][0]["m_value"].decode()
            if controller == "Computer":
                raise NotImplementedError("Computer Player Found")
            elif controller == "None":
                tracker_ids_to_player[event["m_intData"][0]["m_value"]] = None
            else:
                tracker_ids_to_player[event["m_intData"][0]["m_value"]] = event[
                    "m_stringData"
                ][1]["m_value"].decode()

        # Bans
        if event["_event"] == "NNet.Replay.Tracker.SHeroBannedEvent":
            team = Team.LEFT if event["m_controllingTeam"] == 1 else Team.RIGHT
            if firstpick == None:
                firstpick = team
            internal_hero_name = event["m_hero"].decode()
            hero = get_hero_from_internal(internal_hero_name)
            draft.append(DraftAction(DraftActionType.BAN, team, hero))

        # Picks
        if event["_event"] == "NNet.Replay.Tracker.SHeroPickedEvent":

            internal_hero_name = event["m_hero"].decode()
            hero = get_hero_from_internal(internal_hero_name)
            try:
                team = [p for p in players.values() if p["hero"] == hero][0]["team"]
            except IndexError:
                # It's possible a replay got merged with a draft that isn't its own.
                # Let's hope it's a dodge and single-hero exchange, which we can reconstruct later.
                continue
            draft.append(DraftAction(DraftActionType.PICK, team, hero))

        # Level, winner, completeness
        if (
            event["_eventid"] == 10
            and event["m_eventName"].decode() == "EndOfGameTalentChoices"
        ):
            tracker_id = event["m_intData"][0]["m_value"]
            player_id = tracker_ids_to_player[tracker_id]
            if player_id == None:
                continue
            players[player_id]["level"] = event["m_intData"][1]["m_value"]
            players[player_id]["win"] = (
                event["m_stringData"][1]["m_value"].decode() == "Win"
            )
            incomplete = False
        # Core (game time)
        if (
            event["_eventid"] == 1
            and event["_event"] == "NNet.Replay.Tracker.SUnitBornEvent"
            and event["m_unitTypeName"].decode() == "KingsCore"
        ):
            core_ids.append((event["m_unitTagIndex"], event["m_unitTagRecycle"]))
        if (
            event["_eventid"] == 2
            and event["_event"] == "NNet.Replay.Tracker.SUnitDiedEvent"
            and (event["m_unitTagIndex"], event["m_unitTagRecycle"]) in core_ids
        ):
            last_gameloop = event["_gameloop"]
            duration = get_seconds(last_gameloop)

    if len(draft) == 15:
        missing_team = (
            Team.LEFT
            if len([a for a in draft if a.team == Team.LEFT]) == 7
            else Team.RIGHT
        )
        missing_type = (
            DraftActionType.PICK
            if len([a for a in draft if a.type == DraftActionType.PICK]) == 9
            else DraftActionType.BAN
        )
        missing_hero = None
        if missing_type == DraftActionType.PICK:
            heroes_in_draft = [
                action.hero for action in draft if action.type == DraftActionType.PICK
            ]
            missing_hero = [
                p["hero"] for p in players.values() if p["hero"] not in heroes_in_draft
            ][0]

        def is_ok(d):
            for ban_pos in [0, 1, 2, 3, 9, 10]:
                if d[ban_pos].type != DraftActionType.BAN:
                    return False
            for pick_pos in [4, 5, 6, 7, 8, 11, 12, 13, 14, 15]:
                if d[pick_pos].type != DraftActionType.PICK:
                    return False
            for team_pos in [0, 2, 4, 7, 8, 10, 13, 14]:
                if d[team_pos].team != firstpick:
                    return False
            for team_pos in [1, 3, 5, 6, 9, 11, 12, 15]:
                if d[team_pos].team == firstpick:
                    return False
            return True

        def fix_draft(_draft, _missing_move):
            for i in range(16):
                try_draft = _draft[:i] + [_missing_move] + _draft[i:]
                if is_ok(try_draft):
                    _draft = try_draft
                    return _draft
            assert False

        missing_move = DraftAction(missing_type, missing_team, missing_hero)
        draft = fix_draft(draft, missing_move)

    if len(tracker_ids_to_player.items()) == 0:
        raise NotImplementedError(
            "Parsing Sandbox/Escape From Braxis/... replays not supported"
        )

    # Building models
    player_models = ([], [])
    hero_models = ([], [])
    winner = None
    for player_id, player in players.items():
        i = 0 if player["team"] == Team.LEFT else 1
        player_model = Player(player_id, player["name"], player["battletag"])
        player_models[i].append(player_model)
        hero_models[i].append(player["hero"])
        if "win" in player.keys() and player["win"]:
            winner = player["team"]

    return Replay(
        replay_id,
        version,
        gamemode,
        duration,
        date,
        (tuple(player_models[0]), tuple(player_models[1])),
        (tuple(hero_models[0]), tuple(hero_models[1])),
        battleground,
        incomplete,
        winner,
        draft if len(draft) == 16 else None,
    )


def print_replay_contents(filename):
    archive = mpyq.MPQArchive(filename)
    contents = archive.header["user_data_header"]["content"]
    header = protocol96370.decode_replay_header(contents)
    version = Version(
        header["m_version"]["m_baseBuild"],
        header["m_version"]["m_major"],
        header["m_version"]["m_minor"],
        header["m_version"]["m_revision"],
        header["m_version"]["m_build"],
        header["m_version"]["m_flags"],
    )

    protocol = import_heroprotocol(version.base_build)
    if protocol is None:
        archive.file.close()
        raise Exception("Unsupported Build")

    # Details
    details = protocol.decode_replay_details(archive.read_file("replay.details"))

    contents = archive.read_file("replay.details")
    details = protocol.decode_replay_details(contents)
    print(details)

    contents = archive.read_file("replay.initData")
    initdata = protocol.decode_replay_initdata(contents)
    print(
        initdata["m_syncLobbyState"]["m_gameDescription"]["m_cacheHandles"],
    )
    print(initdata)

    contents = archive.read_file("replay.game.events")
    for event in protocol.decode_replay_game_events(contents):
        print(event)

    contents = archive.read_file("replay.message.events")
    for event in protocol.decode_replay_message_events(contents):
        print(event)

    if hasattr(protocol, "decode_replay_tracker_events"):
        contents = archive.read_file("replay.tracker.events")
        for event in protocol.decode_replay_tracker_events(contents):
            print(event)

    contents = archive.read_file("replay.attributes.events")
    attributes = protocol.decode_replay_attributes_events(contents)
    print(attributes)
