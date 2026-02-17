import hashlib
from heroprotocol.versions import protocol96370
import mpyq

from .model import Battleground, Draft, Gamemode, Player, Replay, Team, Version
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

    ai_count = 0
    for player in details["m_playerList"]:
        toon_handle = f"{player['m_toon']['m_region']}-{player['m_toon']['m_programId'].decode()}-{player['m_toon']["m_realm"]}-{player['m_toon']["m_id"]}"
        if toon_handle == "0-\x00\x00\x00\x00-0-0":
            toon_handle = f"AI_{ai_count}"
            ai_count += 1
        players[toon_handle] = {}
        players[toon_handle]["team"] = Team.RIGHT if player["m_teamId"] else Team.LEFT
        players[toon_handle]["name"] = player["m_name"]
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
    tracker_ids_to_player = {}
    core_ids = []
    ais = []
    bans = {Team.LEFT: [], Team.RIGHT: []}
    picks = {Team.LEFT: [], Team.RIGHT: []}
    firstpick = None
    found_heroes = False
    for event in protocol.decode_replay_tracker_events(
        archive.read_file("replay.tracker.events")
    ):
        # Tracker IDs
        if event["_eventid"] == 10 and event["m_eventName"].decode() == "PlayerInit":
            tracker_ids_to_player[event["m_intData"][0]["m_value"]] = event[
                "m_stringData"
            ][1]["m_value"].decode()
            if event["m_stringData"][0]["m_value"].decode() == "Computer":
                ais.append(event["m_intData"][0]["m_value"])

        # Bans
        if event["_event"] == "NNet.Replay.Tracker.SHeroBannedEvent":
            team = Team.LEFT if event["m_controllingTeam"] == 1 else Team.RIGHT
            if firstpick == None:
                firstpick = team
            internal_hero_name = event["m_hero"].decode()
            hero = get_hero_from_internal(internal_hero_name)
            bans[team].append(hero)

        # Picks
        if event["_event"] == "NNet.Replay.Tracker.SHeroPickedEvent":
            wss_id = event["m_controllingPlayer"]
            player_id = wss_to_player[wss_id]
            if "hero" in players[player_id].keys():
                continue
            team = players[player_id]["team"]
            internal_hero_name = event["m_hero"].decode()
            hero = get_hero_from_internal(internal_hero_name)
            picks[team].append(hero)
            players[player_id]["hero"] = hero
            found_heroes = True

        # Heroes, level
        if (
            event["_eventid"] == 10
            and event["m_eventName"].decode() == "EndOfGameTalentChoices"
        ):
            tracker_id = event["m_intData"][0]["m_value"]
            player_id = tracker_ids_to_player[tracker_id]
            players[player_id]["level"] = event["m_intData"][1]["m_value"]
            players[player_id]["win"] = (
                event["m_stringData"][1]["m_value"].decode() == "Win"
            )
            internal_hero_name = (
                event["m_stringData"][0]["m_value"].decode().replace("Hero", "")
            )
            hero = get_hero_from_internal(internal_hero_name)
            players[player_id]["hero"] = hero
            found_heroes = True
            internal_bg_name = event["m_stringData"][2]["m_value"].decode()
            try:
                battleground = get_battleground(internal_bg_name)
            except KeyError:
                battleground = Battleground.OTHER

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

    # Attribute Events
    if not found_heroes and gamemode not in [Gamemode.ARAM, Gamemode.BRAWL]:
        attributes = protocol.decode_replay_attributes_events(
            archive.read_file("replay.attributes.events")
        )
        for tracker_id in tracker_ids_to_player.keys():
            short_name = attributes["scopes"][tracker_id][4002][0]["value"].decode()
            player_id = tracker_ids_to_player[tracker_id]
            if "hero" in players[player_id].keys():
                continue
            team = players[player_id]["team"]
            hero = get_hero_from_short(short_name)
            players[player_id]["hero"] = hero

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
    draft = None
    if len(picks[Team.LEFT]) > 0:
        draft = Draft(bans, picks, firstpick)

    return Replay(
        replay_id,
        version,
        gamemode,
        duration,
        date,
        (tuple(player_models[0]), tuple(player_models[1])),
        (tuple(hero_models[0]), tuple(hero_models[1])),
        battleground,
        winner,
        draft,
    )
