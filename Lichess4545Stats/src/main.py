from src.utility.load_data import DataLoader
from src.utility.stats import rank_players_by_stat


if __name__ == '__main__':
    loader = DataLoader(path='../data/all_seasons/')

    # Rank all active players.
    rank_players_by_stat(loader.players, 'rating', lambda t: set(loader.players[t[0]]['seasons']) & {27, 28, 29, 30, 31})
