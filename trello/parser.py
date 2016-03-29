from trolly.board import Board
from trolly.client import Client

import namingrules
import past_tense_rules
from trello.extendedcard import TrelloExtendedCard
from trello.liststat import TrelloListStat
from trello.graphs import TrelloGraphs
from reporting import SECTION_SEPARATOR
LISTS_UNITS_RULE = "ListsUnitsGraph"


class TrelloParser:

    def __init__(self, trello_config, report, pic_dir):
        self.config = trello_config
        self.api_key = self.config['api_key']
        self.user_oauth_token = self.config['user_oauth_token']
        self.report = report
        self.naming_rules_obj = namingrules.NamingRules()
        self.past_tense_rules_obj = past_tense_rules.PastTenseRules()
        self.trello_lists = {}
        self.pic_dir = pic_dir

    def load_list_data(self, list_name):
        trello_list_stat = TrelloListStat()
        if list_name not in self.trello_lists:
            print("Can't find list '{}' on board".format(list_name))
            return trello_list_stat
        trello_list = self.trello_lists[list_name]
        print("Processing Trello list: " + list_name)
        if trello_list:
            for card in reversed(trello_list.get_cards()):
                print("Processing Trello task: " + card.name)
                extended_card = TrelloExtendedCard(card, self.config, self.report,
                                                   self.naming_rules_obj.naming_rules,
                                                   self.past_tense_rules_obj)
                extended_card.parse_and_add_to_report(list_name)
                trello_list_stat.add_card_stats(extended_card)
        return trello_list_stat

    def add_lists_stats_graph(self, list_names, done_stats, img_path):
            TrelloGraphs.make_lists_stats_graph(self.pic_dir + '/' + self.config['lists_stats_graph_filename'],
                                                list_names, done_stats)
            path = self.naming_rules_obj.naming_rules[LISTS_UNITS_RULE]
            section_path_elements = path.split(SECTION_SEPARATOR)
            section_path_elements.append(self.config['list_stats_graph_tag'].format(img_path))

            self.report.find_or_create_section(self.report.root_section, section_path_elements, 0, False)

    def load_data(self):
        if self.api_key != '' and self.user_oauth_token != '':
            client = Client(self.api_key, self.user_oauth_token)
            board = Board(client, self.config['board_id'])

            self.naming_rules_obj.read_naming_rules(self.config['naming_rules_file'])
            self.past_tense_rules_obj.read_past_tense_rules(self.config['past_tense_rules_file'])

            board_lists = board.get_lists()
            for trello_list in board_lists:
                self.trello_lists[trello_list.name] = trello_list

            done_stats = {}
            list_names = self.config['list_done_names'].split(",")
            for list_name in list_names:
                list_stat = self.load_list_data(list_name)
                done_stats[list_name] = list_stat

            self.load_list_data(self.config['list_failed_name'])
            self.load_list_data(self.config['list_notes_name'])

            img_path = self.pic_dir.split('/')[-1] + "/" + self.config['lists_stats_graph_filename']
            self.add_lists_stats_graph(list_names, done_stats, img_path)
        else:
            print("Empty api_key or user oauth token: skip Trello processing")
