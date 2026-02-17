from datetime import datetime
from enum import Enum, auto


class Version:
    def __init__(self, base_build, major, minor, revision, build, flags):
        self.base_build: int = base_build
        self.major: int = major
        self.minor: int = minor
        self.revision: int = revision
        self.build: int = build
        self.flags: int | None = flags

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.revision}.{self.build}"


class Team(Enum):
    LEFT = auto()
    RIGHT = auto()


class Player:
    def __init__(self, id, display_name, battletag):
        self.id: str = id
        self.display_name: str = display_name
        self.battletag: str = battletag

    def __str__(self):
        return self.battletag


class Gamemode(Enum):
    VERSUS_AI = "Versus A.I."
    PRACTICE = "Practice"
    QUICK_MATCH = "Quick Match"
    UNRANKED_DRAFT = "Unranked"
    BRAWL = "Brawl"
    ARAM = "ARAM"
    CUSTOM = "Custom"
    HERO_LEAGUE = "Hero League"
    TEAM_LEAGUE = "Team League"
    STORM_LEAGUE = "Storm League"
    OTHER = "Other"


class Draft:
    def __init__(self, bans, picks, firstpick):
        self.bans: dict[Team, tuple[Hero, ...]] = bans
        self.picks: dict[Team, tuple[Hero, ...]] = picks
        self.firstpick: Team = firstpick

    def __str__(self):
        return str([str(hero) for hero in self.draft_order()])

    def draft_order(self):
        fp = self.firstpick
        sp = Team.LEFT if fp == Team.RIGHT else Team.RIGHT
        return [
            self.bans[fp][0],
            self.bans[sp][0],
            self.bans[fp][1],
            self.bans[sp][1],
            self.picks[fp][0],
            self.picks[sp][0],
            self.picks[sp][1],
            self.picks[fp][1],
            self.picks[fp][2],
            self.bans[sp][2],
            self.bans[fp][2],
            self.picks[sp][2],
            self.picks[sp][3],
            self.picks[fp][3],
            self.picks[fp][4],
            self.picks[sp][4],
        ]

    def is_ok(self):
        return (
            len(self.bans[Team.LEFT]) == 3
            and len(self.bans[Team.RIGHT]) == 3
            and len(self.picks[Team.LEFT]) == 5
            and len(self.picks[Team.RIGHT]) == 5
        )

    def state(self):
        return "Available" if self.is_ok() else "Incomplete"


class Role(Enum):
    TANK = "Tank"
    BRUISER = "Bruiser"
    RANGED_ASSASSIN = "Ranged Assassin"
    MELEE_ASSASSIN = "Melee Assassin"
    HEALER = "Healer"
    SUPPORT = "Support"


class Hero(Enum):
    ABATHUR = (1, "Abathur", Role.SUPPORT)
    ALARAK = (2, "Alarak", Role.MELEE_ASSASSIN)
    ALEXSTRASZA = (3, "Alexstrasza", Role.HEALER)
    ANA = (4, "Ana", Role.HEALER)
    ANDUIN = (5, "Anduin", Role.HEALER)
    ANUBARAK = (6, "Anub'arak", Role.TANK)
    ARTANIS = (7, "Artanis", Role.BRUISER)
    ARTHAS = (8, "Arthas", Role.TANK)
    AURIEL = (9, "Auriel", Role.HEALER)
    AZMODAN = (10, "Azmodan", Role.RANGED_ASSASSIN)
    BLAZE = (11, "Blaze", Role.TANK)
    BRIGHTWING = (12, "Brightwing", Role.HEALER)
    CASSIA = (13, "Cassia", Role.RANGED_ASSASSIN)
    CHEN = (14, "Chen", Role.BRUISER)
    CHO = (15, "Cho", Role.TANK)
    CHROMIE = (16, "Chromie", Role.RANGED_ASSASSIN)
    DVA = (17, "D.Va", Role.BRUISER)
    DEATHWING = (18, "Deathwing", Role.BRUISER)
    DECKARD_CAIN = (19, "Deckard Cain", Role.HEALER)
    DEHAKA = (20, "Dehaka", Role.BRUISER)
    DIABLO = (21, "Diablo", Role.TANK)
    E_T_C = (22, "E.T.C.", Role.TANK)
    FALSTAD = (23, "Falstad", Role.RANGED_ASSASSIN)
    FENIX = (24, "Fenix", Role.RANGED_ASSASSIN)
    GALL = (25, "Gall", Role.RANGED_ASSASSIN)
    GARROSH = (26, "Garrosh", Role.TANK)
    GAZLOWE = (27, "Gazlowe", Role.BRUISER)
    GENJI = (28, "Genji", Role.RANGED_ASSASSIN)
    GREYMANE = (29, "Greymane", Role.RANGED_ASSASSIN)
    GULDAN = (30, "Gul'dan", Role.RANGED_ASSASSIN)
    HANZO = (31, "Hanzo", Role.RANGED_ASSASSIN)
    HOGGER = (32, "Hogger", Role.BRUISER)
    ILLIDAN = (33, "Illidan", Role.MELEE_ASSASSIN)
    IMPERIUS = (34, "Imperius", Role.BRUISER)
    JAINA = (35, "Jaina", Role.RANGED_ASSASSIN)
    JOHANNA = (36, "Johanna", Role.TANK)
    JUNKRAT = (37, "Junkrat", Role.RANGED_ASSASSIN)
    KAELTHAS = (38, "Kael'thas", Role.RANGED_ASSASSIN)
    KELTHUZAD = (39, "Kel'Thuzad", Role.RANGED_ASSASSIN)
    KERRIGAN = (40, "Kerrigan", Role.MELEE_ASSASSIN)
    KHARAZIM = (41, "Kharazim", Role.HEALER)
    LEORIC = (42, "Leoric", Role.BRUISER)
    LI_LI = (43, "Li Li", Role.HEALER)
    LI_MING = (44, "Li-Ming", Role.RANGED_ASSASSIN)
    LT_MORALES = (45, "Lt. Morales", Role.HEALER)
    LUNARA = (46, "Lunara", Role.RANGED_ASSASSIN)
    LUCIO = (47, "Lúcio", Role.HEALER)
    MAIEV = (48, "Maiev", Role.MELEE_ASSASSIN)
    MALGANIS = (49, "Mal'Ganis", Role.TANK)
    MALFURION = (50, "Malfurion", Role.HEALER)
    MALTHAEL = (51, "Malthael", Role.BRUISER)
    MEDIVH = (52, "Medivh", Role.SUPPORT)
    MEI = (53, "Mei", Role.TANK)
    MEPHISTO = (54, "Mephisto", Role.RANGED_ASSASSIN)
    MURADIN = (55, "Muradin", Role.TANK)
    MURKY = (56, "Murky", Role.MELEE_ASSASSIN)
    NAZEEBO = (57, "Nazeebo", Role.RANGED_ASSASSIN)
    NOVA = (58, "Nova", Role.RANGED_ASSASSIN)
    ORPHEA = (59, "Orphea", Role.RANGED_ASSASSIN)
    PROBIUS = (60, "Probius", Role.RANGED_ASSASSIN)
    QHIRA = (61, "Qhira", Role.MELEE_ASSASSIN)
    RAGNAROS = (62, "Ragnaros", Role.BRUISER)
    RAYNOR = (63, "Raynor", Role.RANGED_ASSASSIN)
    REHGAR = (64, "Rehgar", Role.HEALER)
    REXXAR = (65, "Rexxar", Role.BRUISER)
    SAMURO = (66, "Samuro", Role.MELEE_ASSASSIN)
    SGT_HAMMER = (67, "Sgt. Hammer", Role.RANGED_ASSASSIN)
    SONYA = (68, "Sonya", Role.BRUISER)
    STITCHES = (69, "Stitches", Role.TANK)
    STUKOV = (70, "Stukov", Role.HEALER)
    SYLVANAS = (71, "Sylvanas", Role.RANGED_ASSASSIN)
    TASSADAR = (72, "Tassadar", Role.RANGED_ASSASSIN)
    THE_BUTCHER = (73, "The Butcher", Role.MELEE_ASSASSIN)
    THE_LOST_VIKINGS = (74, "The Lost Vikings", Role.SUPPORT)
    THRALL = (75, "Thrall", Role.BRUISER)
    TRACER = (76, "Tracer", Role.RANGED_ASSASSIN)
    TYCHUS = (77, "Tychus", Role.RANGED_ASSASSIN)
    TYRAEL = (78, "Tyrael", Role.TANK)
    TYRANDE = (79, "Tyrande", Role.HEALER)
    UTHER = (80, "Uther", Role.HEALER)
    VALEERA = (81, "Valeera", Role.MELEE_ASSASSIN)
    VALLA = (82, "Valla", Role.RANGED_ASSASSIN)
    VARIAN = (83, "Varian", Role.BRUISER)
    WHITEMANE = (84, "Whitemane", Role.HEALER)
    XUL = (85, "Xul", Role.BRUISER)
    YREL = (86, "Yrel", Role.BRUISER)
    ZAGARA = (87, "Zagara", Role.RANGED_ASSASSIN)
    ZARYA = (88, "Zarya", Role.SUPPORT)
    ZERATUL = (89, "Zeratul", Role.MELEE_ASSASSIN)
    ZULJIN = (90, "Zul'jin", Role.RANGED_ASSASSIN)

    def __init__(self, id, display_name, role):
        self.id: int = id
        self.display_name: str = display_name
        self.role: Role = role

    def __str__(self):
        return self.display_name


class Battleground(Enum):
    ALTERAC_PASS = ("Alterac Pass", 3)
    BATTLEFIELD_OF_ETERNITY = ("Battlefield of Eternity", 2)
    BLACKHEARTS_BAY = ("Blackheart's Bay", 3)
    BRAXIS_HOLDOUT = ("Braxis Holdout", 2)
    BRAXIS_OUTPOST = ("Braxis Outpost", 1)
    CHECKPOINT_HANAMURA = ("Checkpoint: Hanamura", 0)
    CURSED_HOLLOW = ("Cursed Hollow", 3)
    DRAGON_SHIRE = ("Dragon Shire", 3)
    ESCAPE_FROM_BRAXIS = ("Escape From Braxis", 0)
    ESCAPE_FROM_BRAXIS_HEROIC = ("Escape From Braxis (Heroic)", 0)
    GARDEN_OF_TERROR = ("Garden of Terror", 3)
    HANAMURA_TEMPLE = ("Hanamura Temple", 2)
    HAUNTED_MINES = ("Haunted Mines", 2)
    INDUSTRIAL_DISTRICT = ("Industrial District", 1)
    INFERNAL_SHRINES = ("Infernal Shrines", 3)
    LOST_CAVERN = ("Lost Cavern", 1)
    PULL_PARTY = ("Pull Party", 0)
    SILVER_CITY = ("Silver City", 1)
    SKY_TEMPLE = ("Sky Temple", 3)
    TOMB_OF_THE_SPIDER_QUEEN = ("Tomb of the Spider Queen", 3)
    TOWERS_OF_DOOM = ("Towers of Doom", 3)
    VOLSKAYA_FOUNDRY = ("Volskaya Foundry", 3)
    WARHEAD_JUNCTION = ("Warhead Junction", 3)
    OTHER = ("Other", 0)

    def __init__(self, display_name, lanes):
        self.display_name: str = display_name
        self.lanes: int = lanes

    def __str__(self):
        return self.display_name


class Replay:
    def __init__(
        self,
        replay_id: str,
        version: Version,
        gamemode: Gamemode,
        duration: int | None,
        date: datetime,
        players: tuple[tuple[Player, ...], tuple[Player, ...]],
        heroes: tuple[tuple[Hero, ...], tuple[Hero, ...]],
        battleground: Battleground,
        winner: Team | None = None,
        draft: Draft | None = None,
    ):
        self.id: str = replay_id
        self.version: Version = version
        self.gamemode: Gamemode = gamemode
        self.duration: int | None = duration
        self.date = date
        self.players: tuple[tuple[Player, ...], tuple[Player, ...]] = players
        self.heroes: tuple[tuple[Hero, ...], tuple[Hero, ...]] = heroes
        self.battleground: Battleground = battleground
        self.winner: Team | None = winner
        self.draft: Draft | None = draft

    def __str__(self):
        return str(
            {
                "Version": str(self.version),
                "Gamemode": str(self.gamemode),
                "Duration": str(self.duration),
                "Date": str(self.date),
                "Players": ", ".join(
                    [str(player) for team in self.players for player in team]
                ),
                "Heroes": ", ".join(
                    [str(hero) for team in self.heroes for hero in team]
                ),
                "Battleground": str(self.battleground),
                "Winner": str(self.winner),
                "Draft": self.draft.state() if self.draft else "None",
            }
        )

    def get_heroprotocol(self):
        from .util import import_heroprotocol

        return import_heroprotocol(self.version.base_build)
