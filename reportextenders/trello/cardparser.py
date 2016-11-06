import re

from trolly.card import Card

from config import Config
from reportextenders.trello.cardstatsparser import TrelloCardStatsParser
from reportextenders.trello.parsedcard import TrelloParsedCard
from sectionstats import UnitStats

SECTION_SEPARATOR = '/'
NO_LABEL_RULE = "NoLabel"
UNKNOWN_LABEL_RULE = "UnknownLabel"
COMMENT_TYPE_TEXT = "commentCard"
LABELS_HASH_TAG = "labels"
LABEL_NAME_HASH_TAG = "name"
ACTION_DATA_HASH_TAG = "data"
ACTION_DATA_TEXT_HASH_TAG = "text"
ACTION_TYPE_HASH_TAG = "type"
COMMENT_AS_PLANNED = " - as planned"
COMMENT_NOT_DONE = 'NOT DONE - '
POMELLO_INFO = "Pomello Log"


class TrelloCardParser(Card):
    def __init__(self, card, section_entries, report, naming_rules, past_tense_rules_obj):
        super(Card, self).__init__(card.client)
        self.id = card.id
        self.name = card.name
        self.base_uri = '/cards/' + self.id
        self.section_entries = section_entries
        self.card_stats_parser = TrelloCardStatsParser(self.section_entries)
        self.report = report
        self.naming_rules = naming_rules
        self.past_tense_rules_obj = past_tense_rules_obj

    def __get_actions_json(self):
        return self.fetch_json(self.base_uri + '/actions')

    def __get_desc_json(self):
        return self.fetch_json(self.base_uri + '/desc')

    def __get_desc_lines(self):
        desc = self.__get_desc_json()
        desc_lines = []
        if desc is not None and desc != '':
            desc_lines = desc['_value'].split("\n")
        return desc_lines

    def __process_checklists(self):
        children = []
        checklists = self.get_checklists()
        for checklist in (checklists if checklists else []):
            items = checklist.get_items()

            for item in items:
                prefix, postfix = '', ''
                value = self.subst_urls(item['name'])
                if item['state'] == 'complete':
                    postfix = COMMENT_AS_PLANNED
                    value = self.past_tense_rules_obj.convert_to_past(value)
                else:
                    prefix = COMMENT_NOT_DONE
                children.append(prefix + value + postfix)
        return children

    def __process_actions_log(self):
        children = []
        actions = self.__get_actions_json()
        unit_stats = UnitStats()
        for action in (reversed(actions) if actions else []):
            #  process only comments, ignore other actions
            if action[ACTION_TYPE_HASH_TAG] == COMMENT_TYPE_TEXT:
                comment = action[ACTION_DATA_HASH_TAG][ACTION_DATA_TEXT_HASH_TAG]
                if POMELLO_INFO in comment:
                    # TODO: process comments to broken pomodoros
                    continue  # skip Pomello service information
                elif self.card_stats_parser.has_pomodoro_info(comment):
                    comment_unit_stats = self.card_stats_parser.process_stats_in_comment(comment)
                    unit_stats.add(comment_unit_stats)
                else:
                    children.append(comment)
        return children, unit_stats

    def __get_card_path(self):
        labels = self.get_card_information()[LABELS_HASH_TAG]
        if not labels:
            path = self.naming_rules.get_path(NO_LABEL_RULE)
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

    def parse(self):
        parsed_card = TrelloParsedCard(self.__get_card_path())
        desc_lines = self.__get_desc_lines()

        stats_in_title = self.card_stats_parser.process_stats_in_title(self.name)  # use raw card title
        if stats_in_title:
            parsed_card.unit_stats.add(stats_in_title)

        section_path_elements = parsed_card.path.split(SECTION_SEPARATOR)
        if section_path_elements:
            parsed_card.title = TrelloCardParser.\
                clean_title(Config.get_section_param(self.section_entries, 'title_clean_regexp'), self.name).strip()
            parsed_card.title_past = self.past_tense_rules_obj.convert_to_past(parsed_card.title)

            for desc_line in filter(lambda s: "http" not in s, desc_lines):
                if "http" in desc_line:
                    parsed_card.title += " " + self.subst_urls(desc_line)
                    parsed_card.title_past += " " + self.subst_urls(desc_line)
                elif desc_line:
                    parsed_card.add_child(desc_line)

        parsed_card.children.extend(self.__process_checklists())

        (children, stats) = self.__process_actions_log()
        parsed_card.children.extend(children)
        parsed_card.unit_stats.add(stats)

        return parsed_card
