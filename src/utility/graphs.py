import math

import networkx as nx

from itertools import combinations

from bokeh.io import output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, LabelSet
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.transform import linear_cmap
from bokeh.palettes import Blues8, Purples8

from utility.load_data import sorted_tuple


"""
Credits: So, far most of the code here is just copy-pasted and adapted from 

https://melaniewalsh.github.io/Intro-Cultural-Analytics/06-Network-Analysis/02-Making-Network-Viz-with-Bokeh.html
"""


def color_map(rating):
    if rating < 1600:
        return 'blue'
    elif rating < 1800:
        return 'green'
    elif rating < 2000:
        return 'red'
    elif rating < 2200:
        return 'purple'
    else:
        return 'yellow'


def generate_team_graph(teams, players, min_seasons=0, min_seasons_together=0):
    g = nx.Graph()

    # Select all players that are eligible i.e. that have played a given number of seasons in the league.
    eligible_players = {player for (player, stats) in players.items() if stats['games'] >= min_seasons}

    # Add all eligible players to the graph.
    node_sizes = dict()
    ratings = dict()

    for player in eligible_players:
        g.add_node(player)
        node_sizes[player] = len(players[player]['seasons'])
        ratings[player] = players[player]['rating'] if players[player]['rating'] != -1 else 1500

    nx.set_node_attributes(g, name='seasons', values=node_sizes)
    nx.set_node_attributes(g, name='ratings', values=ratings)

    edges = dict()

    for (team, stats) in teams.items():
        for player_a, player_b in combinations(stats['players'], 2):
            if player_a in eligible_players and player_b in eligible_players:
                player_a, player_b = sorted_tuple(player_a, player_b)

                if (player_a, player_b) in edges:
                    edges[(player_a, player_b)] += 1
                else:
                    edges[(player_a, player_b)] = 1

    for (player_a, player_b), weight in edges.items():
        if weight >= min_seasons_together:
            g.add_edge(player_a, player_b, weight=weight)

    title = 'Games played between players.'
    HOVER_TOOLTIPS = [("Player", "@index"), ("Rating", "@ratings")]
    color_palette = Purples8

    plot = figure(tooltips=HOVER_TOOLTIPS,
                  tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                  x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

    # Create a network graph object with spring layout
    # https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
    network_graph = from_networkx(g, nx.spring_layout, scale=10, center=(0, 0))

    # Set node size and color
    minimum_value_color = min(network_graph.node_renderer.data_source.data['ratings'])
    maximum_value_color = max(network_graph.node_renderer.data_source.data['ratings'])
    network_graph.node_renderer.glyph = Circle(size='seasons',
                                               fill_color=linear_cmap('ratings', color_palette, minimum_value_color,
                                                                      maximum_value_color))

    # Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width='weight')

    # Add network graph to the plot
    plot.renderers.append(network_graph)

    """
    x, y = zip(*network_graph.layout_provider.graph_layout.values())
    node_labels = list(g.nodes())
    source = ColumnDataSource({'x': x, 'y': y, 'name': [node_labels[i] for i in range(len(x))]})
    labels = LabelSet(x='x', y='y', text='name', source=source, background_fill_color='white', text_font_size='10px',
                      background_fill_alpha=.7)
    plot.renderers.append(labels)
    """

    output_notebook()
    show(plot)


def generate_match_up_graph(match_ups, players, min_games=0):
    g = nx.Graph()

    # Select all players that are eligible i.e. that have played a given number of games in the league.
    eligible_players = {player for (player, stats) in players.items() if stats['games'] >= min_games}

    # Add all eligible players to the graph.
    node_sizes = dict()
    ratings = dict()

    for player in eligible_players:
        g.add_node(player)
        node_sizes[player] = math.sqrt(players[player]['games'])
        ratings[player] = players[player]['rating'] if players[player]['rating'] != -1 else 1500

    nx.set_node_attributes(g, name='games', values=node_sizes)
    nx.set_node_attributes(g, name='ratings', values=ratings)

    # Add edges for all pairs of players that have played at least one game against each other.
    edge_sizes = dict()

    for player, opponents in match_ups.items():
        if player in eligible_players:
            for opponent, stats in opponents.items():
                if opponent in eligible_players:
                    g.add_edge(player, opponent, weight=stats['num_games'])

                    edge_sizes[(player, opponent)] = stats['num_games']

    nx.set_edge_attributes(g, name='games', values=edge_sizes)

    title = 'Games played between players.'
    HOVER_TOOLTIPS = [("Player", "@index"), ("Rating", "@ratings")]
    color_palette = Purples8

    plot = figure(tooltips=HOVER_TOOLTIPS,
                  tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                  x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

    # Create a network graph object with spring layout
    # https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
    network_graph = from_networkx(g, nx.spring_layout, scale=10, center=(0, 0))

    # Set node size and color
    minimum_value_color = min(network_graph.node_renderer.data_source.data['ratings'])
    maximum_value_color = max(network_graph.node_renderer.data_source.data['ratings'])
    network_graph.node_renderer.glyph = Circle(size='games', fill_color=linear_cmap('ratings', color_palette, minimum_value_color, maximum_value_color))

    # Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width='games')

    # Add network graph to the plot
    plot.renderers.append(network_graph)

    """
    x, y = zip(*network_graph.layout_provider.graph_layout.values())
    node_labels = list(g.nodes())
    source = ColumnDataSource({'x': x, 'y': y, 'name': [node_labels[i] for i in range(len(x))]})
    labels = LabelSet(x='x', y='y', text='name', source=source, background_fill_color='white', text_font_size='10px',
                      background_fill_alpha=.7)
    plot.renderers.append(labels)
    """

    output_notebook()
    show(plot)
