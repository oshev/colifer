import re

from trolly.card import Card

from reporting import SECTION_SEPARATOR
from trello.pomodoros import TrelloPomodoros
from sectionstat import SectionStat

NO_LABEL_RULE = "NoLabel"
UNKNOWN_LABEL_RULE = "UnknownLabel"
COMMENT_TYPE_TEXT = "commentCard"
LABELS_HASH_TAG = "labels"
LABEL_NAME_HASH_TAG = "name"
ACTION_DATA_HASH_TAG = "data"
ACTION_DATA_TEXT_HASH_TAG = "text"
ACTION_TYPE_HASH_TAG = "type"
NOT_DONE_LABEL = "NotDone"
COMMENT_AS_PLANNED = " - as planned"
COMMENT_NOT_DONE = 'NOT DONE - '
POMELLO_INFO = "Pomello Log"


class TrelloExtendedCard(Card):
    def __init__(self, card, trello_config, report, naming_rules, past_tense_rules_obj):
        super(Card, self).__init__(card.client)
        self.id = card.id
        self.name = card.name
        self.base_uri = '/cards/' + self.id
        self.trello_pomodoros = TrelloPomodoros()
        self.report = report
        self.naming_rules = naming_rules
        self.past_tense_rules_obj = past_tense_rules_obj
        self.stats = SectionStat()
        self.config = trello_config

    def get_actions_json(self):
        return self.fetch_json(self.base_uri + '/actions')

    def get_desc_json(self):
        return self.fetch_json(self.base_uri + '/desc')

    def get_desc_lines(self):
        desc = self.get_desc_json()
        desc_lines = []
        if desc is not None and desc != '':
            desc_lines = desc['_value'].split("\n")
        return desc_lines

    def process_checklists(self, section_path_elements):
        checklists = self.get_checklists()
        for checklist in checklists:
            items = checklist.get_items()

            for item in items:
                prefix, postfix = '', ''
                if item['state'] == 'complete':
                    postfix = COMMENT_AS_PLANNED
                else:
                    prefix = COMMENT_NOT_DONE
                value = self.subst_urls(item['name'])
                value = self.past_tense_rules_obj.convert_to_past(value)
                section_path_elements.append(prefix + value + postfix)
                self.report.find_or_create_section(self.report.root_section,
                                                   section_path_elements, 0, False)
                section_path_elements.pop()

    def process_actions(self, section_path_elements, this_section):
        actions = self.get_actions_json()

        for action in reversed(actions):
            if action[ACTION_TYPE_HASH_TAG] == COMMENT_TYPE_TEXT:
                comment = action[ACTION_DATA_HASH_TAG][ACTION_DATA_TEXT_HASH_TAG]
                if self.trello_pomodoros.has_pomodoro_info(comment):
                    pomodoros_stat = self.trello_pomodoros.process_pomodoros_in_comment(comment)
                    self.stats.pomodoros_stat.add_pomodoros(pomodoros_stat)  # update card stats
                    self.trello_pomodoros.add_pomodoros_to_section(this_section, pomodoros_stat)  # set section stats
                elif POMELLO_INFO in comment:
                    continue  # skip Pomello service information
                else:
                    section_path_elements.append(comment)
                    self.report.find_or_create_section(self.report.root_section,
                                                       section_path_elements, 0, False)
                    section_path_elements.pop()

    def get_card_path(self, list_name):
        labels = self.get_card_information()[LABELS_HASH_TAG]
        path = ""
        if not labels:
            if NO_LABEL_RULE in self.naming_rules:
                path = self.naming_rules[NO_LABEL_RULE]
        else:
            if list_name == self.config['list_failed_name']:
                path = self.naming_rules[NOT_DONE_LABEL]
            else:
                labels_list = []
                for label in labels:
                    labels_list.append(label[LABEL_NAME_HASH_TAG])
                sorted_labels = ','.join(sorted(labels_list))
                if sorted_labels in self.naming_rules:
                    path = self.naming_rules[sorted_labels]
                else:
                    print("Unknown label {}!".format(sorted_labels))
                    path = self.naming_rules[UNKNOWN_LABEL_RULE]
        return path

    # TODO: add card chain processing: clean title, substitute urls, change the first verb to past tense

    @staticmethod
    def clean_title(title):  # removes Pomello's marks
        title = re.sub("^\s*\d+\s+✓\s*", "", title)
        title = re.sub("\(-?\d+(\.\d+)?\)\s*", "", title)
        title = re.sub("\[\d+\]\s*", "", title)
        return title

    @staticmethod
    def subst_urls(text):
        return re.sub(r"(https*:[^\s]+)", r"<a href='\1'>link</a>", text, flags=re.IGNORECASE)

    # TODO: Separate parse from adding to report. Parse should only create an add object.
    # TODO: Adding to report must be in trello parser.

    def parse_and_add_to_report(self, list_name):
        desc_lines = self.get_desc_lines()
        path = self.get_card_path(list_name)

        pomodoros_in_title = self.trello_pomodoros.process_pomodoros_in_title(self.name)  # use raw card title
        if pomodoros_in_title:
            self.stats.pomodoros_stat.add_pomodoros(pomodoros_in_title)  # update card stats
            if self.stats.pomodoros_stat.not_done > 0:
                path = self.naming_rules[NOT_DONE_LABEL] + SECTION_SEPARATOR + list_name

        section_path_elements = path.split(SECTION_SEPARATOR)
        if section_path_elements:
            title = TrelloExtendedCard.clean_title(self.name)
            title = self.past_tense_rules_obj.convert_to_past(title)
            section_path_elements.append(title)
            this_section = self.report.find_or_create_section(self.report.root_section,
                                                              section_path_elements, 0, False)
            if pomodoros_in_title:
                self.trello_pomodoros.add_pomodoros_to_section(this_section, pomodoros_in_title)  # set section stats

            for desc_line in desc_lines:
                if desc_line != '':
                    desc_line = self.subst_urls(desc_line)
                    section_path_elements.append(desc_line)
                    self.report.find_or_create_section(self.report.root_section,
                                                       section_path_elements, 0, False)
                    section_path_elements.pop()

            checklists = self.get_checklists()
            if checklists is not None:
                self.process_checklists(section_path_elements)

            actions = self.get_actions_json()  # = comments in the task
            if actions is not None and len(actions) > 0:
                self.process_actions(section_path_elements, this_section)
