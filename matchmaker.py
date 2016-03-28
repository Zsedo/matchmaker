# ENGINE
# -------------------------

from common import Queuer, Player, max_mmr, min_mmr
from typing import Iterable, List
import random

TEAM_SIZE = 5


class Lobby:
    def __init__(self, team_1: List[Player], team_2: List[Player]):
        self.team_1 = team_1
        self.team_2 = team_2

    def __repr__(self):
        return "Lobby: " + str(self.team_1) + " VS " + str(self.team_2)


class MatchMaker:

    def __init__(self, find_lobby):
        self._find_lobby = find_lobby

    def find_lobbies(self, queue: List[Queuer], on_found_lobby) -> List[Lobby]:
        lobbies = []
        while True:
            found = self._find_lobby(queue)
            if found is not None:
                t1, t2 = found
                lobby = Lobby([q.player for q in t1], [q.player for q in t2])
                lobbies.append(lobby)
                on_found_lobby(t1+t2)
            else:
                return lobbies


def find_by_sorted_mmr(queue: List[Queuer]) -> Lobby:
    if len(queue) < TEAM_SIZE*2:
        return None
    copy = list(queue)
    ind = random.randint(0, len(copy) - TEAM_SIZE*2)
    copy.sort(key=lambda q: q.player.mmr)
    t1 = []
    t2 = []
    for i in range(TEAM_SIZE):
        t1.append(copy[(ind + 2*i) % len(copy)])
        t2.append(copy[(ind + 2*i + 1) % len(copy)])
    return t1, t2


def limited_find_by_sorted_mmr(queue: List[Queuer]) -> Lobby:
    num_tries = 50
    mmr_diff_boundary = 300
    if len(queue) < TEAM_SIZE*2:
        return None
    for i in range(num_tries):
        t1, t2 = find_by_sorted_mmr(queue)
        players = [q.player for q in t1+t2]
        max_mmr_diff = abs(max_mmr(players) - min_mmr(players))
        if max_mmr_diff < mmr_diff_boundary:
            return t1, t2
    return None


def _get_random_slice(array: Iterable, slice_size: int) -> list:
    copy = list(array)
    random.shuffle(copy)
    return copy[0: slice_size]


def _pick_teams_random(queuers: Iterable[Queuer]) -> (List[Player], List[Player]):
    picked_queuers = _get_random_slice(queuers, TEAM_SIZE * 2)
    team_1 = picked_queuers[0: TEAM_SIZE]
    team_2 = picked_queuers[TEAM_SIZE: TEAM_SIZE * 2]
    return team_1, team_2


def _pick_teams_unfair(queuers: Iterable[Queuer]) -> (List[Player], List[Player]):
    picked_queuers = _get_random_slice(queuers, TEAM_SIZE * 2)
    picked_queuers.sort(key=lambda p: p.mmr)
    team_1 = picked_queuers[0: TEAM_SIZE]
    team_2 = picked_queuers[TEAM_SIZE: TEAM_SIZE * 2]
    return team_1, team_2


def _pick_teams_simple(queue: List[Queuer]):
    t1 = queue[0: TEAM_SIZE]
    t2 = queue[TEAM_SIZE: TEAM_SIZE*2]
    return [(t1, t2)]


simple_matchmaker = MatchMaker(find_by_sorted_mmr)
advanced_matchmaker = MatchMaker(limited_find_by_sorted_mmr)
