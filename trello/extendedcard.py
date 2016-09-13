import re

from trolly.card import Card

from reporting import SECTION_SEPARATOR
from sectionstats import SectionStats
from trello.cardstats import TrelloCardStatsParser

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
        self.config = trello_config
        self.card_stats_parser = TrelloCardStatsParser(self.config)
        self.report = report
        self.naming_rules = naming_rules
        self.past_tense_rules_obj = past_tense_rules_obj
        self.stats = SectionStats()

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
                value = self.subst_urls(item['name'])
                if item['state'] == 'complete':
                    postfix = COMMENT_AS_PLANNED
                    value = self.past_tense_rules_obj.convert_to_past(value)
                else:
                    prefix = COMMENT_NOT_DONE
                section_path_elements.append(prefix + value + postfix)
                self.report.find_or_create_section(self.report.root_section,
                                                   section_path_elements, 0, False)
                section_path_elements.pop()

    def process_actions(self, section_path_elements, this_section):
        actions = self.get_actions_json()

        for action in reversed(actions):
            if action[ACTION_TYPE_HASH_TAG] == COMMENT_TYPE_TEXT:
                comment = action[ACTION_DATA_HASH_TAG][ACTION_DATA_TEXT_HASH_TAG]
                if self.card_stats_parser.has_pomodoro_info(comment):
                    pomodoros_stat = self.card_stats_parser.process_stats_in_comment(comment)
                    self.stats.unit_stats.add(pomodoros_stat)  # update card stats
                    self.card_stats_parser.add_stats_to_section(this_section, pomodoros_stat)  # set section stats
                elif POMELLO_INFO in comment:
                    continue  # skip Pomello service information
                else:
                    section_path_elements.append(comment)
                    self.report.find_or_create_section(self.report.root_section,
                                                       section_path_elements, 0, False)
                    section_path_elements.pop()

    def get_card_path(self, list_name):
        labels = self.get_card_information()[LABELS_HASH_TAG]
        if not labels:
            path = self.naming_rules.get_path(NO_LABEL_RULE)
        else:
            if list_name == self.config['list_failed_name']:
                path = self.naming_rules.get_path(NOT_DONE_LABEL)
            else:
                labels_list = []
                for label in labels:
                    labels_list.append(label[LABEL_NAME_HASH_TAG])
                sorted_labels = ','.join(sorted(labels_list))
                path = self.naming_rules.get_path(sorted_labels, self.name)
                if path is None:
                    print("Unknown label {}!".format(sorted_labels))
                    path = self.naming_rules.get_path(UNKNOWN_LABEL_RULE)
        return path if path is not None else ""

    # TODO: add card chain processing: clean title, substitute urls, change the first verb to past tense

    @staticmethod
    def clean_title(clean_regexp, title):  # removes Pomello's marks
        title = re.sub(clean_regexp, "", title)
        return title

    @staticmethod
    def subst_urls(text):
        return re.sub(r"(https*:[^\s]+)", r"<a href='\1'>link</a>", text, flags=re.IGNORECASE)

    # TODO: Separate parse from adding to report. Parse should only create an add object.
    # TODO: Adding to report must be in Trello parser.

    def parse_and_add_to_report(self, list_name):
        desc_lines = self.get_desc_lines()
        path = self.get_card_path(list_name)

        stats_in_title = self.card_stats_parser.process_stats_in_title(self.name)  # use raw card title
        if stats_in_title:
            self.stats.unit_stats.add(stats_in_title)  # update card stats
            print(self.stats)
            if self.stats.unit_stats.not_done() > 0:
                # TODO: move only part of the card which is not done to not done section
                # path = self.naming_rules.get_path(NOT_DONE_LABEL) + SECTION_SEPARATOR + list_name
                pass

        section_path_elements = path.split(SECTION_SEPARATOR)
        if section_path_elements:
            title = TrelloExtendedCard.clean_title(self.config['title_clean_regexp'], self.name)
            if not self.stats.unit_stats or self.stats.unit_stats.not_done == 0:
                # don't convert verbs to past for failed tasks
                title = self.past_tense_rules_obj.convert_to_past(title)

            for url_line in filter(lambda s: "http" in s, desc_lines):
                title += " " + self.subst_urls(url_line)

            section_path_elements.append(title)
            this_section = self.report.find_or_create_section(self.report.root_section,
                                                              section_path_elements, 0, False)
            if stats_in_title:
                self.card_stats_parser.add_stats_to_section(this_section, stats_in_title)  # set section stats

            for desc_line in filter(lambda s: "http" not in s, desc_lines):
                if desc_line != '':
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
