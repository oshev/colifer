from trolly.client import Client
from trolly.board import Board
from trolly.list import List
from trolly.card import Card
from trolly.checklist import Checklist
from trolly.member import Member
from trolly import ResourceUnavailable
from reporting import SECTION_SEPARATOR

NO_LABEL_RULE = "NoLabel"

class TrelloParser:

    api_key = ''
    user_oauth_token = ''

    def __init__(self, api_key, oauth_token):
        self.api_key = api_key
        self.user_oauth_token = oauth_token

    @staticmethod
    def load_list_data(naming_rules, report, lists, list_name, add_to_name):
        for list in lists:
            if list.name == list_name:
                for card in list.get_cards():
                    print("Processing Trello task: " + card.name)
                    labels = card.get_card_information()["labels"]
                    rules = []
                    if not labels:
                        if naming_rules[NO_LABEL_RULE] is not None:
                            rules.append(naming_rules[NO_LABEL_RULE])
                    else:
                        for label in labels:
                            if naming_rules[label["name"]] is not None:
                                rules.append(naming_rules[label["name"]])
                    for rule in rules:
                        section_path_elements = rule.split(SECTION_SEPARATOR)
                        if section_path_elements:
                            section_path_elements.append(add_to_name + card.name)

                            section = report.find_or_create_section(report.root_section,
                                                                    section_path_elements, 0, False)


    @staticmethod
    def read_naming_rules(naming_rules_filename):
        naming_rules = {}
        lines = [line.strip() for line in open(naming_rules_filename)]
        for row in lines:
            if row != '' and not row.startswith('#'):
                elements = row.split('=')
                if len(elements) == 2:
                    naming_rules[elements[0]] = elements[1]
        return naming_rules
        # .split(SECTION_SEPARATOR)

    def load_data(self, board_id, list_done_name, list_failed_name, naming_rules_filename, report):
        if self.api_key != '' and self.user_oauth_token != '':
            client = Client(self.api_key, self.user_oauth_token)
            board = Board(client, board_id)

            naming_rules = self.read_naming_rules(naming_rules_filename)
            lists = board.get_lists()
            self.load_list_data(naming_rules, report, lists, list_done_name, '')
            self.load_list_data(naming_rules, report, lists, list_failed_name, 'NOT DONE - ')

