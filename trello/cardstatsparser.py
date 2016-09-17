import re

from sectionstats import SectionStats
from sectionstats import UnitStats

MAX_CHARS_FOR_POMODORO_STATS = 20


class TrelloCardStatsParser:

    def __init__(self, trello_config):
        self.config = trello_config

    @staticmethod
    def has_pomodoro_info(comment):
        return "pomodoro" in comment.lower()

    @staticmethod
    def add_unit_stats_to_section(section, unit_stats, stop_at=None):
        if not section:
            return
        if section.stats is None:
            section.stats = SectionStats()
        section.stats.unit_stats.add(unit_stats)
        if not stop_at or stop_at != section:
            TrelloCardStatsParser.add_unit_stats_to_section(section.parent, unit_stats, stop_at)

    @staticmethod
    def process_stats_in_comment(comment):
        pomodoro_stat = UnitStats()

        comment_lower = comment.lower()
        if "pomodoro" in comment_lower and len(comment) < MAX_CHARS_FOR_POMODORO_STATS:
            if "broken" in comment_lower:
                pomodoro_stat.broken_pomodoros += 1
            else:
                elements = comment_lower.split(' ')
                int_value = None
                for element in elements:
                    if element and element.isdigit():
                        int_value = int(element)
                        break
                pomodoro_stat.done_pomodoros += int_value if int_value else 1
        return pomodoro_stat

    @staticmethod
    def get_group_int(re_obj):
        if re_obj and len(re_obj.groups()) > 0 and re_obj.groups()[0].replace(".", "", 1).replace("-", "").isdigit():
            return float(re_obj.groups()[0])
        else:
            return 0.0

    @staticmethod
    def get_target_num(regexp, text):
        groups = re.search(regexp, text)
        return TrelloCardStatsParser.get_group_int(groups)

    def process_stats_in_title(self, title):
        planned = TrelloCardStatsParser.get_target_num(self.config['title_planned_regexp'], title)
        done_cucumbers = TrelloCardStatsParser.get_target_num(self.config['title_done_cucumbers_regexp'], title)
        done_pomodoros = TrelloCardStatsParser.get_target_num(self.config['title_done_pomodoros_regexp'], title)
        if planned or done_cucumbers or done_pomodoros:
            unit_stats = UnitStats()
            unit_stats.planned += planned
            unit_stats.done_cucumbers += done_cucumbers
            unit_stats.done_pomodoros += done_pomodoros
            unit_stats.not_done = max(unit_stats.planned - unit_stats.done_units(), 0)
            unit_stats.done_units_plan = min(unit_stats.done_units(), unit_stats.planned)
            return unit_stats
        return None

