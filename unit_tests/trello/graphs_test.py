from trello.graphs import TrelloGraphs
import colifer

# TODO

TrelloGraphs.make_lists_stats_graph(colifer.config['Files']['pic_dir'] +
                                    '/' +
                                    colifer.config['Trello']['lists_stats_graph_filename'],
                                    colifer.config['Trello']['list_done_names'].split(","),
                                    [])

# units_done = [1, 2, 3, 4, 5, 6, 7]
# pomodoros_done = [5, 4, 3, 6, 7, 8, 9]
# units_failed = [2, 2, 3, 9, 1, 8, 10]

