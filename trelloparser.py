from trolly.client import Client
from trolly.board import Board
from trolly.card import Card

from reporting import SECTION_SEPARATOR
import sectionstat

NO_LABEL_RULE = "NoLabel"
COMMENT_TYPE_TEXT = "commentCard"
LABELS_HASH_TAG = "labels"
LABEL_NAME_HASH_TAG = "name"
ACTION_DATA_HASH_TAG = "data"
ACTION_DATA_TEXT_HASH_TAG = "text"
ACTION_TYPE_HASH_TAG = "type"

class ExtendedCard(Card):

    def __init__(self, card):

        super(Card, self).__init__(card.client)

        self.id = card.id
        self.name = card.name

        self.base_uri = '/cards/' + self.id

    def get_actions_json(self):
        return self.fetch_json(self.base_uri + '/actions')

class TrelloParser:

    api_key = ''
    user_oauth_token = ''

    def __init__(self, api_key, oauth_token):
        self.api_key = api_key
        self.user_oauth_token = oauth_token

    @staticmethod
    def process_pomodoros(pomodoro_stat, comment):
        comment_lower = comment.lower()
        if "pomodoro" in comment_lower:
            if "broken" in comment_lower:
                pomodoro_stat.broken += 1
            elif "double" in comment_lower:
                pomodoro_stat.done_double += 1
                pomodoro_stat.done += 2
            elif "2" in comment_lower:
                pomodoro_stat.done_single += 2
                pomodoro_stat.done += 2
            elif "3" in comment_lower:
                pomodoro_stat.done_single += 3
                pomodoro_stat.done += 3
            else:
                pomodoro_stat.done_single += 1
                pomodoro_stat.done += 1
            return True
        else:
            return False

    @staticmethod
    def propagate_pomodoros_to_parent(section, pomodoros):
        if section.parent is not None:
            if section.parent.stats is None:
                section.parent.stats = sectionstat.SectionStat()
            if section.parent.stats.pomodoros_stat is None:
                section.parent.stats.pomodoros_stat = sectionstat.PomodorosStat()
            section.parent.stats.pomodoros_stat.add_pomodoros(pomodoros)

            TrelloParser.propagate_pomodoros_to_parent(section.parent, pomodoros)

    @staticmethod
    def process_checklists(report, section_path_elements, checklists):

        for checklist in checklists:

            items = checklist.get_items()

            for item in items:
                section_path_elements.append(item['name'])
                report.find_or_create_section(report.root_section,
                                              section_path_elements, 0, False)
                section_path_elements.pop()

    @staticmethod
    def process_actions(report, section_path_elements, this_section, actions):
        pomodoros = sectionstat.PomodorosStat()

        for action in reversed(actions):
            if action[ACTION_TYPE_HASH_TAG] == COMMENT_TYPE_TEXT:
                if not TrelloParser.process_pomodoros(pomodoros,
                                                      action[ACTION_DATA_HASH_TAG]
                                                            [ACTION_DATA_TEXT_HASH_TAG]):

                    section_path_elements.append(action[ACTION_DATA_HASH_TAG]
                                                       [ACTION_DATA_TEXT_HASH_TAG])
                    report.find_or_create_section(report.root_section,
                                                  section_path_elements, 0, False)
                    section_path_elements.pop()
        if pomodoros.is_not_zero():
            this_section.stats = sectionstat.SectionStat()
            this_section.stats.pomodoros_stat = pomodoros
            TrelloParser.propagate_pomodoros_to_parent(this_section, pomodoros)

    @staticmethod
    def load_list_data(naming_rules, report, trello_lists, list_name, add_to_name):
        for trello_list in trello_lists:
            if trello_list.name == list_name:
                for card in reversed(trello_list.get_cards()):
                    extended_card = ExtendedCard(card)
                    actions = extended_card.get_actions_json()
                    print("Processing Trello task: " + card.name)
                    labels = card.get_card_information()[LABELS_HASH_TAG]

                    rules = []
                    if not labels:
                        if naming_rules[NO_LABEL_RULE] is not None:
                            rules.append(naming_rules[NO_LABEL_RULE])
                    else:
                        for label in labels:
                            if naming_rules[label[LABEL_NAME_HASH_TAG]] is not None:
                                rules.append(naming_rules[label[LABEL_NAME_HASH_TAG]])
                    for rule in rules:
                        section_path_elements = rule.split(SECTION_SEPARATOR)
                        if section_path_elements:
                            section_path_elements.append(add_to_name + card.name)

                            this_section = report.find_or_create_section(report.root_section,
                                                                         section_path_elements, 0, False)

                            checklists = card.get_checklists()
                            if checklists is not None:
                                TrelloParser.process_checklists(report, section_path_elements, checklists)

                            if actions is not None and len(actions) > 0:
                                TrelloParser.process_actions(report, section_path_elements, this_section, actions)

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

    def load_data(self, board_id, list_done_name, list_failed_name, naming_rules_filename, report):
        if self.api_key != '' and self.user_oauth_token != '':
            client = Client(self.api_key, self.user_oauth_token)
            board = Board(client, board_id)

            naming_rules = self.read_naming_rules(naming_rules_filename)
            trello_lists = board.get_lists()
            self.load_list_data(naming_rules, report, trello_lists, list_done_name, '')
            self.load_list_data(naming_rules, report, trello_lists, list_failed_name, 'NOT DONE - ')

