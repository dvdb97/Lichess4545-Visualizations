import tabulate


def get_players_with_n_games(players, n):
    """
    Collects all players with atleast n games played in the league.

    :param players: The dictionary containing player-specific data.
    :param n: The minimum number of games that a player has to have played in order to qualify.
    :return: Returns a list of player names that satisify this criterion.
    """
    players_filtered = list()

    for player in players:
        if players[player]['games'] >= n:
            players_filtered.append(player)

    return players_filtered


def get_players_with_n_seasons(players, n):
    """
    Collects all players with at least n seasons played in the league.

    :param players: The dictionary containing player-specific data.
    :param n: The minimum number of season that a player has to have played in order to qualify.
    :return: Returns a list of player names that satisfy this criterion.
    """
    players_filtered = list()

    for player in players:
        if len(players[player]['seasons']) >= n:
            players_filtered.append(player)

    return players_filtered


def get_players_sorted_by_stat(players, stat, filter_f):
    players_mapped = map(lambda tup: (tup[0], tup[-1][stat]), players.items())

    return sorted(filter(filter_f, players_mapped), key=lambda t: t[-1], reverse=True)


def rank_players_by_stat(players, stat, filter_f, top=None):
    ranked = get_players_sorted_by_stat(players, stat, filter_f)
    table = []

    for idx, (player, value) in enumerate(ranked):
        if top is not None and idx >= top:
            break

        table.append([idx + 1, player, value])

    return tabulate.tabulate(table, tablefmt='html', headers=['rank', 'name', stat])
