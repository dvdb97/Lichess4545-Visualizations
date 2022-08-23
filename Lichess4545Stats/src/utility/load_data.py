import requests
import json
import tqdm
import sys
from lichess.api import users_by_ids


def sorted_tuple(w, b):
    """
    Return the two given player names as a tuple
    with both entries sorted alphabetically.

    :param w: The name of the white player.
    :param b: The name of the black player.
    """
    if w < b:
        return w, b

    return b, w


class DataLoader:
    def __init__(self, seasons=None, path=None):
        self.match_ups = dict()
        self.players = dict()
        self.teams = dict()

        if path is None and seasons is not None:
            self.__load_data(seasons)

        if path is not None:
            self.load_data(path)

    def __load_data(self, seasons):
        """
        Requests the game data via the lichess4545 api and extracts the desired data.

        :param seasons: The list of seasons to include.
        """
        url = 'https://www.lichess4545.com/api/get_season_games/'

        for season in seasons:
            print('Season:', season)

            # Request all games for the given season from the lichess4545 website.
            page = requests.get(url=url, params={'league': 'team4545', 'season': season})
            games = json.loads(page.text)['games']

            for game in tqdm.tqdm(games):
                player_w = game['white'].lower()
                player_b = game['black'].lower()
                result = game['result']

                self.__add_players(player_w, player_b, season)
                self.__add_match_up(player_w, player_b, result)
                self.__add_players_to_teams(player_w, game['white_team'], player_b, game['black_team'], season)

        self.__get_player_ratings()

    def __get_player_ratings(self):
        """
        Gets the ratings for all players in a single step. This turned out to be faster when done in one step
        instead of requesting it on a player-by-player basis.
        """
        for p_data in tqdm.tqdm(users_by_ids(list(self.players.keys()))):
            if 'disabled' not in p_data:
                rating = p_data['perfs']['classical']['rating']
            else:
                rating = -1

            self.players[p_data['id']]['rating'] = rating

    def __add_player_to_team(self, player, team, season):
        """
        Adds a player to the list of players that played for a certain team.

        :param player: The player's name.
        :param team: The team name.
        :param season: The season. Required for exact identification because some team names were used multiple times.
        """
        team = team + '_' + str(season)

        if team not in self.teams:
            self.teams[team] = {'season': season, 'players': list()}

        if player not in self.teams[team]['players']:
            self.teams[team]['players'].append(player)

    def __add_players_to_teams(self, player_w, team_w, player_b, team_b, season):
        """
        Adds two players to their respective teams.

        :param player_w: The white player's name.
        :param team_w: The team name for the white player.
        :param player_b: The black player's name.
        :param team_b: The team name for the black player.
        :param season: The season. Required for exact identification because some team names were used multiple times.
        """
        self.__add_player_to_team(player_w, team_w, season)
        self.__add_player_to_team(player_b, team_b, season)

    def __add_player(self, player, season):
        """
        Adds a player to the list of players and counts the number of seasons and games they played.

        :param player: The player's name
        :param season: The number of the season in which they played.
        """
        if player not in self.players:
            self.players[player] = {'seasons': list(), 'games': 0}

        self.players[player]['games'] += 1

        if season not in self.players[player]['seasons']:
            self.players[player]['seasons'].append(season)

    def __add_players(self, player_w, player_b, season):
        """
        Adds two players to the list of players and counts the number of seasons and games they played.

        :param player_w: The white player's name.
        :param player_b: The black player's name.
        :param season: The number of the season in which they played.
        """
        self.__add_player(player_w, season)
        self.__add_player(player_b, season)

    def __add_match_up(self, player_w, player_b, result):
        """
        Counts the number of games and corresponding scores between two players.

        :param player_w: The white player's name.
        :param player_b: The black player's name.
        :param result: The games result. One of {'1-0', '0-1', '1/2-1/2'}
        """
        a, b = sorted_tuple(player_w, player_b)

        if a not in self.match_ups:
            self.match_ups[a] = dict()

        if b not in self.match_ups[a]:
            self.match_ups[a][b] = {'num_games': 0, 'score_a': 0, 'score_b': 0}

        match_up = self.match_ups[a][b]
        match_up['num_games'] += 1

        if result != '1/2-1/2':
            winner = player_w if result == '1-0' else player_b

            match_up['score_a'] += 1 if a == winner else 0
            match_up['score_b'] += 1 if b == winner else 0
        else:
            match_up['score_a'] += 0.5
            match_up['score_b'] += 0.5

    def save_data(self, path):
        with open(path + 'players.json', 'w') as f:
            f.write(json.dumps(self.players))

        with open(path + 'teams.json', 'w') as f:
            f.write(json.dumps(self.teams))

        with open(path + 'matchups.json', 'w') as f:
            f.write(json.dumps(self.match_ups))

    def load_data(self, path):
        with open(path + 'players.json', 'r') as f:
            self.players = json.loads(f.read())

        with open(path + 'teams.json', 'r') as f:
            self.teams = json.loads(f.read())

        with open(path + '/matchups.json', 'r') as f:
            self.match_ups = json.loads(f.read())


if __name__ == '__main__':
    dl = DataLoader(range(29, 32))
