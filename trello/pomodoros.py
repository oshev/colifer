from sectionstat import PomodorosStat
from sectionstat import SectionStat
import re

TITLE_PATTERN_POM_UNITS = '^.*\((-?\d+(\.\d+)?)\).*$'
TITLE_PATTERN_POM_DONE = '^.*\[(\d+)\]\s*$'
MAX_CHARS_FOR_POMODORO_STATS = 20


class TrelloPomodoros:

    def __init__(self):
        super().__init__()

    @staticmethod
    def has_pomodoro_info(comment):
        return "pomodoro" in comment.lower()

    @staticmethod
    def add_pomodoros_to_section(section, pomodoros_stat):
        if not section:
            return
        if section.stats is None:
            section.stats = SectionStat()
        section.stats.pomodoros_stat.add_pomodoros(pomodoros_stat)
        TrelloPomodoros.add_pomodoros_to_section(section.parent, pomodoros_stat)

    @staticmethod
    def process_pomodoros_in_comment(comment):
        pomodoro_stat = PomodorosStat()

        comment_lower = comment.lower()
        if "pomodoro" in comment_lower and len(comment) < MAX_CHARS_FOR_POMODORO_STATS:
            if "broken" in comment_lower:
                pomodoro_stat.broken += 1
            else:
                elements = comment_lower.split(' ')
                int_value = None
                for element in elements:
                    if element and element.isdigit():
                        int_value = int(element)
                        break
                pomodoro_stat.done += int_value if int_value else 1
        return pomodoro_stat

    @staticmethod
    def get_group_int(re_obj):
        if re_obj and len(re_obj.groups()) > 0 and re_obj.groups()[0].replace(".", "", 1).replace("-", "").isdigit():
            return float(re_obj.groups()[0])
        else:
            return 0.0

    @staticmethod
    def process_pomodoros_in_title(title):
        units = re.search(TITLE_PATTERN_POM_UNITS, title)
        units_pom_num = TrelloPomodoros.get_group_int(units)
        done = re.search(TITLE_PATTERN_POM_DONE, title)
        done_pom_num = TrelloPomodoros.get_group_int(done)
        if units or done:
            pomodoro_stat = PomodorosStat()
            pomodoro_stat.done += done_pom_num
            if units_pom_num > 0:
                pomodoro_stat.units += units_pom_num
            else:
                pomodoro_stat.not_done += -units_pom_num
            return pomodoro_stat
        return None

