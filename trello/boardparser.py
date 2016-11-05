import re

from trolly.board import Board
from trolly.client import Client

import namingrules
import past_tense_rules
from reporting import SECTION_SEPARATOR
from sectionstats import UnitStats
from trello.cardparser import TrelloCardParser
from trello.cardstatsparser import TrelloCardStatsParser
from trello.graphs import TrelloGraphs

LISTS_UNITS_RULE = "ListsUnitsGraph"
NOT_DONE_LABEL = "NotDone"
UNFINISHED_COMMENT = "Unfinished"


class TrelloBoardParser:

    def __init__(self, config, report, pic_dir):
        self.config = config
        self.api_key = self.config.get_param('Trello.api_key')
        self.user_oauth_token = self.config.get_param('Trello.user_oauth_token')
        self.report = report

        self.naming_rules = namingrules.NamingRules()
        self.naming_rules.read_naming_rules(self.config.get_param('Trello.naming_rules_file'))

        self.past_tense_rules_obj = past_tense_rules.PastTenseRules()
        self.past_tense_rules_obj.read_past_tense_rules(self.config.get_param('Trello.past_tense_rules_file'))

        self.trello_lists = {}
        self.pic_dir = pic_dir
        self.list_group_separator_regexp = self.config.get_param('Trello.list_group_separator_regexp')
        self.not_done_section = self.report.find_or_create_section(self.report.root_section,
                                                                   self.naming_rules.get_path(NOT_DONE_LABEL).
                                                                   split(SECTION_SEPARATOR), 0, False)

    def is_group_separator(self, title):
        return re.match(self.list_group_separator_regexp, title)

    def add_parsed_card_to_report(self, parsed_card, list_name):

        section_path_elements = parsed_card.path.split(SECTION_SEPARATOR)
        section_path_elements.append(parsed_card.title_past)
        this_section = self.report.find_or_create_section(self.report.root_section,
                                                          section_path_elements, 0, False)
        TrelloCardStatsParser.add_unit_stats_to_section(this_section, parsed_card.unit_stats)
        children_section_path_elements = section_path_elements

        if parsed_card.unit_stats.not_done > 0:
            # add NOT DONE comment to unfinished tasks
            section_path_elements.append(UNFINISHED_COMMENT)
            self.report.find_or_create_section(self.report.root_section, section_path_elements, 0, False)
            # add failed tickets to FAILED section as well
            not_done_path = self.naming_rules.get_path(NOT_DONE_LABEL) + SECTION_SEPARATOR + list_name
            failed_section_path_elements = not_done_path.split(SECTION_SEPARATOR)
            failed_section_path_elements.append(parsed_card.title)
            failed_section = self.report.find_or_create_section(self.report.root_section,
                                                                failed_section_path_elements, 0, False)
            # don't propagate stats of failed tasks up, we already considered their stats in the main section
            propagation_stop_section = self.not_done_section
            TrelloCardStatsParser.add_unit_stats_to_section(failed_section, parsed_card.unit_stats,
                                                            stop_at=propagation_stop_section)
            if not parsed_card.unit_stats.done_units():
                children_section_path_elements = failed_section_path_elements

        for child in parsed_card.children:
            children_section_path_elements.append(child)
            self.report.find_or_create_section(self.report.root_section,
                                               children_section_path_elements, 0, False)
            children_section_path_elements.pop()

    def load_list_data(self, list_name):
        trello_list_stat = UnitStats()
        if list_name not in self.trello_lists:
            print("Can't find list '{}' on board".format(list_name))
            return trello_list_stat
        trello_list = self.trello_lists[list_name]
        print("Processing Trello list: " + list_name)
        if trello_list:
            for card in trello_list.get_cards():
                print("Processing Trello task: " + card.name)
                if self.is_group_separator(card.name):
                    print("\tis group separator, skipping")
                else:
                    extended_card = TrelloCardParser(card, self.config, self.report,
                                                     self.naming_rules,
                                                     self.past_tense_rules_obj)
                    parsed_card = extended_card.parse()
                    self.add_parsed_card_to_report(parsed_card, list_name)
                    trello_list_stat.add(parsed_card.unit_stats)
        return trello_list_stat

    def add_lists_stats_graph(self, list_names, done_stats, img_path):
            TrelloGraphs.make_lists_stats_graph(self.pic_dir + '/' +
                                                self.config.get_param('Trello.lists_stats_graph_filename'),
                                                list_names, done_stats)
            path = self.naming_rules.get_path(LISTS_UNITS_RULE)
            section_path_elements = path.split(SECTION_SEPARATOR)
            section_path_elements.append(self.config.get_param('Trello.list_stats_graph_tag').format(img_path))

            self.report.find_or_create_section(self.report.root_section, section_path_elements, 0, False)

    def load_data(self):
        if self.api_key != '' and self.user_oauth_token != '':
            client = Client(self.api_key, self.user_oauth_token)
            board = Board(client, self.config.get_param('Trello.board_id'))

            board_lists = board.get_lists()
            for trello_list in board_lists:
                self.trello_lists[trello_list.name] = trello_list

            done_stats = {}
            list_names = self.config.get_param('Trello.list_done_names').split(",")
            for list_name in list_names:
                list_stat = self.load_list_data(list_name)
                done_stats[list_name] = list_stat

            self.load_list_data(self.config.get_param('Trello.list_notes_name'))

            img_path = self.pic_dir.split('/')[-1] + "/" + self.config.get_param('Trello.lists_stats_graph_filename')
            self.add_lists_stats_graph(list_names, done_stats, img_path)
        else:
            print("Empty api_key or user oauth token: skip Trello processing")
