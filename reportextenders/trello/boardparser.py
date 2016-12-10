import re

from trolly.board import Board
from trolly.client import Client

import namingrules
import past_tense_rules
from config import Config
from reportextenders.report_extender import ReportExtender
from reportextenders.trello.cardparser import TrelloCardParser
from reportextenders.trello.cardstatsparser import TrelloCardStatsParser
from reportextenders.trello.trello_graphs import TrelloGraphs
from sectionstats import UnitStats

SECTION_SEPARATOR = '/'
LISTS_UNITS_RULE = "ListsUnitsGraph"
NOT_DONE_LABEL = "NotDone"
UNFINISHED_COMMENT = "Unfinished"


class TrelloBoardParser(ReportExtender):

    def __init__(self, section_entries):
        super().__init__(section_entries)
        if Config.get_section_param(section_entries, "enabled"):
            self.api_key = Config.get_section_param(section_entries, 'api_key')
            self.user_oauth_token = Config.get_section_param(section_entries, 'user_oauth_token')

            self.naming_rules = namingrules.NamingRules()
            self.naming_rules.read_naming_rules(Config.get_section_param(section_entries, 'naming_rules_file'))

            self.past_tense_rules_obj = past_tense_rules.PastTenseRules()
            self.past_tense_rules_obj.read_past_tense_rules(
                Config.get_section_param(section_entries, 'past_tense_rules_file'))
            self.trello_board_id = Config.get_section_param(section_entries, 'board_id')
            self.trello_list_done_names = Config.get_section_param(section_entries, 'list_done_names')
            self.trello_list_notes_name = Config.get_section_param(section_entries, 'list_notes_name')
            self.list_stats_graph_tag = Config.get_section_param(section_entries, 'list_stats_graph_tag')
            self.lists_stats_graph_filename = Config.get_section_param(section_entries, 'lists_stats_graph_filename')

            self.trello_lists = {}
            self.list_group_separator_regexp = Config.get_section_param(section_entries, 'list_group_separator_regexp')
            self.not_done_section = None
        else:
            self.api_key = None

    def extend_report(self, report, report_parameters):
        if not self.api_key or not self.user_oauth_token:
            return
        self.not_done_section = report.find_or_create_section(report.root_section,
                                                              self.naming_rules.get_path(NOT_DONE_LABEL).
                                                              split(SECTION_SEPARATOR), False)
        client = Client(self.api_key, self.user_oauth_token)
        board = Board(client, self.trello_board_id)

        board_lists = board.get_lists()
        for trello_list in board_lists:
            self.trello_lists[trello_list.name] = trello_list

        done_stats = {}
        list_names = self.trello_list_done_names.split(",")
        for list_name in list_names:
            list_stat = self.load_list_data(report, list_name)
            done_stats[list_name] = list_stat

        self.load_list_data(report, self.trello_list_notes_name)

        full_img_path = report_parameters.pic_dir + "/" + self.lists_stats_graph_filename
        relative_img_path = report_parameters.pic_dir.split('/')[-1] + "/" + self.lists_stats_graph_filename
        self.add_lists_stats_graph(report, list_names, done_stats, full_img_path, relative_img_path)

    def is_group_separator(self, title):
        return re.match(self.list_group_separator_regexp, title)

    def add_parsed_card_to_report(self, report, parsed_card, list_name):

        section_path_elements = parsed_card.path.split(SECTION_SEPARATOR)
        section_path_elements.append(parsed_card.title_past)
        this_section = report.find_or_create_section(report.root_section, section_path_elements, False)
        TrelloCardStatsParser.add_unit_stats_to_section(this_section, parsed_card.unit_stats)
        children_section_path_elements = section_path_elements

        if parsed_card.unit_stats.not_done > 0:
            # add NOT DONE comment to unfinished tasks
            section_path_elements.append(UNFINISHED_COMMENT)
            report.find_or_create_section(report.root_section, section_path_elements, False)
            # add failed tickets to FAILED section as well
            not_done_path = self.naming_rules.get_path(NOT_DONE_LABEL) + SECTION_SEPARATOR + list_name
            failed_section_path_elements = not_done_path.split(SECTION_SEPARATOR)
            failed_section_path_elements.append(parsed_card.title)
            failed_section = report.find_or_create_section(report.root_section, failed_section_path_elements, False)
            # don't propagate stats of failed tasks up, we already considered their stats in the main section
            propagation_stop_section = self.not_done_section
            TrelloCardStatsParser.add_unit_stats_to_section(failed_section, parsed_card.unit_stats,
                                                            stop_at=propagation_stop_section)
            if not parsed_card.unit_stats.done_units():
                children_section_path_elements = failed_section_path_elements

        for child in parsed_card.children:
            children_section_path_elements.append(child)
            report.find_or_create_section(report.root_section, children_section_path_elements, False)
            children_section_path_elements.pop()

    def load_list_data(self, report, list_name):
        trello_list_stat = UnitStats()
        if list_name not in self.trello_lists:
            print("Can't find list '{}' on board".format(list_name))
            return trello_list_stat
        trello_list = self.trello_lists[list_name]
        print("Processing Trello LIST: " + list_name)
        if trello_list:
            for card in trello_list.get_cards():
                print("Processing Trello task: " + card.name)
                if self.is_group_separator(card.name):
                    print("\tis group separator, skipping")
                else:
                    extended_card = TrelloCardParser(card, self.section_entries, report,
                                                     self.naming_rules,
                                                     self.past_tense_rules_obj)
                    parsed_card = extended_card.parse()
                    self.add_parsed_card_to_report(report, parsed_card, list_name)
                    trello_list_stat.add(parsed_card.unit_stats)
        return trello_list_stat

    def add_lists_stats_graph(self, report, list_names, done_stats, full_img_path, relative_img_path):
            TrelloGraphs.make_lists_stats_graph(full_img_path, list_names, done_stats)
            path = self.naming_rules.get_path(LISTS_UNITS_RULE)
            section_path_elements = path.split(SECTION_SEPARATOR)
            section_path_elements.append(self.list_stats_graph_tag.format(relative_img_path))

            report.find_or_create_section(report.root_section, section_path_elements, False)
