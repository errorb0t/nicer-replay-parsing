from datetime import datetime
import pkgutil
import re

import heroprotocol.versions

from .model import Battleground, Gamemode, Hero


_GAMEMODE_DICT = {
    50001: Gamemode.QUICK_MATCH,
    50021: Gamemode.VERSUS_AI,
    50031: Gamemode.BRAWL,
    50041: Gamemode.PRACTICE,
    50051: Gamemode.UNRANKED_DRAFT,
    50061: Gamemode.HERO_LEAGUE,
    50071: Gamemode.TEAM_LEAGUE,
    50091: Gamemode.STORM_LEAGUE,
    50101: Gamemode.ARAM,
    -1: "Custom",
}
_SHORT_HERO_DICT = {
    "Abat": Hero.ABATHUR,
    "Alar": Hero.ALARAK,
    "Alex": Hero.ALEXSTRASZA,
    "HANA": Hero.ANA,
    "Andu": Hero.ANDUIN,
    "Anub": Hero.ANUBARAK,
    "Arts": Hero.ARTANIS,
    "Arth": Hero.ARTHAS,
    "Auri": Hero.AURIEL,
    "Azmo": Hero.AZMODAN,
    "Fire": Hero.BLAZE,
    "Faer": Hero.BRIGHTWING,
    "Amaz": Hero.CASSIA,
    "Chen": Hero.CHEN,
    "CCho": Hero.CHO,
    "Chro": Hero.CHROMIE,
    "DVA0": Hero.DVA,
    "DEAT": Hero.DEATHWING,
    "DECK": Hero.DECKARD_CAIN,
    "Deha": Hero.DEHAKA,
    "Diab": Hero.DIABLO,
    "L90E": Hero.E_T_C,
    "Fals": Hero.FALSTAD,
    "FENX": Hero.FENIX,
    "Gall": Hero.GALL,
    "Garr": Hero.GARROSH,
    "Tink": Hero.GAZLOWE,
    "Genj": Hero.GENJI,
    "Genn": Hero.GREYMANE,
    "Guld": Hero.GULDAN,
    "Hanz": Hero.HANZO,
    "HOGG": Hero.HOGGER,
    "Illi": Hero.ILLIDAN,
    "IMPE": Hero.IMPERIUS,
    "Jain": Hero.JAINA,
    "Crus": Hero.JOHANNA,
    "Junk": Hero.JUNKRAT,
    "Kael": Hero.KAELTHAS,
    "KelT": Hero.KELTHUZAD,
    "Kerr": Hero.KERRIGAN,
    "Monk": Hero.KHARAZIM,
    "Leor": Hero.LEORIC,
    "LiLi": Hero.LI_LI,
    "Wiza": Hero.LI_MING,
    "Medi": Hero.LT_MORALES,
    "Drya": Hero.LUNARA,
    "Luci": Hero.LUCIO,
    "Maie": Hero.MAIEV,
    "MalG": Hero.MALGANIS,
    "Malf": Hero.MALFURION,
    "MALT": Hero.MALTHAEL,
    "Mdvh": Hero.MEDIVH,
    "HMEI": Hero.MEI,
    "MEPH": Hero.MEPHISTO,
    "Mura": Hero.MURADIN,
    "Murk": Hero.MURKY,
    "Witc": Hero.NAZEEBO,
    "Nova": Hero.NOVA,
    "ORPH": Hero.ORPHEA,
    "Prob": Hero.PROBIUS,
    "NXHU": Hero.QHIRA,
    "Ragn": Hero.RAGNAROS,
    "Rayn": Hero.RAYNOR,
    "Rehg": Hero.REHGAR,
    "Rexx": Hero.REXXAR,
    "Samu": Hero.SAMURO,
    "Sgth": Hero.SGT_HAMMER,
    "Barb": Hero.SONYA,
    "Stit": Hero.STITCHES,
    "STUK": Hero.STUKOV,
    "Sylv": Hero.SYLVANAS,
    "Tass": Hero.TASSADAR,
    "Butc": Hero.THE_BUTCHER,
    "Lost": Hero.THE_LOST_VIKINGS,
    "Thra": Hero.THRALL,
    "Tra0": Hero.TRACER,
    "Tych": Hero.TYCHUS,
    "Tyrl": Hero.TYRAEL,
    "Tyrd": Hero.TYRANDE,
    "Uthe": Hero.UTHER,
    "VALE": Hero.VALEERA,
    "Demo": Hero.VALLA,
    "Vari": Hero.VARIAN,
    "WHIT": Hero.WHITEMANE,
    "Necr": Hero.XUL,
    "YREL": Hero.YREL,
    "Zaga": Hero.ZAGARA,
    "Zary": Hero.ZARYA,
    "Zera": Hero.ZERATUL,
    "ZULJ": Hero.ZULJIN,
}
_INTERNAL_HERO_DICT = {
    "Abathur": Hero.ABATHUR,
    "Alarak": Hero.ALARAK,
    "Alexstrasza": Hero.ALEXSTRASZA,
    "Ana": Hero.ANA,
    "Anduin": Hero.ANDUIN,
    "Anubarak": Hero.ANUBARAK,
    "Artanis": Hero.ARTANIS,
    "Arthas": Hero.ARTHAS,
    "Auriel": Hero.AURIEL,
    "Azmodan": Hero.AZMODAN,
    "Firebat": Hero.BLAZE,
    "FaerieDragon": Hero.BRIGHTWING,
    "Butcher": Hero.CASSIA,
    "Amazon": Hero.CHEN,
    "Chen": Hero.CHO,
    "Cho": Hero.CHROMIE,
    "Chromie": Hero.DVA,
    "Deathwing": Hero.DEATHWING,
    "Dehaka": Hero.DECKARD_CAIN,
    "Deckard": Hero.DEHAKA,
    "Diablo": Hero.DIABLO,
    "DVa": Hero.E_T_C,
    "L90ETC": Hero.FALSTAD,
    "Falstad": Hero.FENIX,
    "Fenix": Hero.GALL,
    "Gall": Hero.GARROSH,
    "Garrosh": Hero.GAZLOWE,
    "Tinker": Hero.GENJI,
    "Genji": Hero.GREYMANE,
    "Greymane": Hero.GULDAN,
    "Guldan": Hero.HANZO,
    "Hanzo": Hero.HOGGER,
    "Hogger": Hero.ILLIDAN,
    "Illidan": Hero.IMPERIUS,
    "Imperius": Hero.JAINA,
    "Jaina": Hero.JOHANNA,
    "Crusader": Hero.JUNKRAT,
    "Junkrat": Hero.KAELTHAS,
    "Kaelthas": Hero.KELTHUZAD,
    "KelThuzad": Hero.KERRIGAN,
    "Kerrigan": Hero.KHARAZIM,
    "Monk": Hero.LEORIC,
    "Leoric": Hero.LI_LI,
    "LiLi": Hero.LI_MING,
    "Wizard": Hero.LT_MORALES,
    "LostVikings": Hero.LUNARA,
    "Lucio": Hero.LUCIO,
    "Medic": Hero.MAIEV,
    "Dryad": Hero.MALGANIS,
    "Maiev": Hero.MALFURION,
    "Malfurion": Hero.MALTHAEL,
    "MalGanis": Hero.MEDIVH,
    "Malthael": Hero.MEI,
    "Medivh": Hero.MEPHISTO,
    "MeiOW": Hero.MURADIN,
    "Mephisto": Hero.MURKY,
    "Muradin": Hero.NAZEEBO,
    "Murky": Hero.NOVA,
    "WitchDoctor": Hero.ORPHEA,
    "Nova": Hero.PROBIUS,
    "Orphea": Hero.QHIRA,
    "Probius": Hero.RAGNAROS,
    "NexusHunter": Hero.RAYNOR,
    "Ragnaros": Hero.REHGAR,
    "Raynor": Hero.REXXAR,
    "Rehgar": Hero.SAMURO,
    "Rexxar": Hero.SGT_HAMMER,
    "Samuro": Hero.SONYA,
    "SgtHammer": Hero.STITCHES,
    "Barbarian": Hero.STUKOV,
    "Stitches": Hero.SYLVANAS,
    "Stukov": Hero.TASSADAR,
    "Sylvanas": Hero.THE_BUTCHER,
    "Tassadar": Hero.THE_LOST_VIKINGS,
    "Thrall": Hero.THRALL,
    "Tracer": Hero.TRACER,
    "Tychus": Hero.TYCHUS,
    "Tyrael": Hero.TYRAEL,
    "Tyrande": Hero.TYRANDE,
    "Uther": Hero.UTHER,
    "Valeera": Hero.VALEERA,
    "DemonHunter": Hero.VALLA,
    "Varian": Hero.VARIAN,
    "Whitemane": Hero.WHITEMANE,
    "Necromancer": Hero.XUL,
    "Yrel": Hero.YREL,
    "Zagara": Hero.ZAGARA,
    "Zarya": Hero.ZARYA,
    "Zeratul": Hero.ZERATUL,
    "Zuljin": Hero.ZULJIN,
    "NONE": None,
}
_BATTLEGROUND_DICT = {
    "BattlefieldOfEternity": Battleground.BATTLEFIELD_OF_ETERNITY,
    "BlackheartsBay": Battleground.BLACKHEARTS_BAY,
    "BraxisHoldout": Battleground.BRAXIS_HOLDOUT,
    "CursedHollow": Battleground.CURSED_HOLLOW,
    "DragonShire": Battleground.DRAGON_SHIRE,
    "HauntedWoods": Battleground.GARDEN_OF_TERROR,
    "Hanamura": Battleground.HANAMURA_TEMPLE,
    "HauntedMines": Battleground.HAUNTED_MINES,
    "Shrines": Battleground.INFERNAL_SHRINES,
    "ControlPoints": Battleground.SKY_TEMPLE,
    "Crypts": Battleground.TOMB_OF_THE_SPIDER_QUEEN,
    "TowersOfDoom": Battleground.TOWERS_OF_DOOM,
    "Warhead Junction": Battleground.WARHEAD_JUNCTION,
    "Volskaya": Battleground.VOLSKAYA_FOUNDRY,
    "AlteracPass": Battleground.ALTERAC_PASS,
    "EscapeFromBraxis": Battleground.ESCAPE_FROM_BRAXIS,
    "IndustrialDistrict": Battleground.INDUSTRIAL_DISTRICT,
    "LostCavern": Battleground.LOST_CAVERN,
    "PullParty": Battleground.PULL_PARTY,
    "SilverCity": Battleground.SILVER_CITY,
    "BraxisOutpost": Battleground.BRAXIS_OUTPOST,
    "HanamuraPayloadPush": Battleground.CHECKPOINT_HANAMURA,
    "EscapeFromBraxis(Heroic)": Battleground.ESCAPE_FROM_BRAXIS_HEROIC,
}


def import_heroprotocol(base_build):
    try:
        protocol = __import__(
            "heroprotocol.versions", fromlist=[f"protocol{base_build}"]
        )
        protocol = getattr(protocol, f"protocol{base_build}")
    except (ImportError, AttributeError):

        # unsupported base build, use previous build
        all_versions = [
            module_name
            for _, module_name, _ in pkgutil.iter_modules(
                heroprotocol.versions.__path__
            )
        ]
        fallback_build = int(all_versions[-1][-5:])

        try:
            protocol = __import__(
                "heroprotocol.versions", fromlist=[f"protocol{fallback_build}"]
            )
            protocol = getattr(protocol, f"protocol{fallback_build}")
        except (ImportError, AttributeError):
            return None

    return protocol


def get_gamemode(gamemode_id: int):
    try:
        gamemode = _GAMEMODE_DICT[gamemode_id]
    except KeyError:
        gamemode = Gamemode.OTHER
    return gamemode


def get_battleground(internal_name):
    return _BATTLEGROUND_DICT[internal_name]


def get_seconds(loops):
    return (loops - 610) / 16


def get_date(time_utc):
    return datetime.fromtimestamp((time_utc // 10000 - 11644473600000) / 1000)


def get_hero_from_internal(internal_name):
    return _INTERNAL_HERO_DICT[internal_name]


def get_hero_from_short(short_name):
    return _SHORT_HERO_DICT[short_name]


def get_battletag(lobby_data, player_name):
    tag = ""
    to_search = b"%s#(\\d{4,8})" % player_name
    r = re.compile(to_search)
    s = r.search(lobby_data)
    if s:
        tag = s.groups(0)[0].decode("utf-8")
        player_name = player_name.decode("utf-8")
        return f"{player_name}#{tag}"
