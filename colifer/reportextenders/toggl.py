import requests

from config import Config
from reportextenders.report_extender import ReportExtender
from sectionstats import SectionStats
from sectionstats import UnitStats
from datetime import datetime
from datetime import timedelta
from tag_order import TagOrder
from reporting import Report
from namingrules import NamingRules
import past_tense_rules

REPORT_PATH_SEPARATOR = '/'
SECTIONSTAT_PATH_SEPARATOR = '$'
CHARACTERS_IN_DATE = 10
MIN_POMODORO_IN_SECONDS = 24*60
MAX_POMODORO_IN_SECONDS = 27*60


class TogglEntriesParser(ReportExtender):
    def __init__(self, section_entries):
        super().__init__(section_entries)
        if Config.get_section_param(section_entries, "enabled"):
            self.auth_token = Config.get_section_param(section_entries, "auth_token")
            self.headers = {'Authorization': 'Basic ' + self.auth_token,
                            'Cache-Control': 'no-cache',
                            'Content-Type': 'application/json'}
            self.entries_endpoint = Config.get_section_param(section_entries, "entries_endpoint")
            self.projects_endpoint = Config.get_section_param(section_entries, "projects_endpoint")
            self.tag_order = TagOrder(Config.get_section_param(section_entries, "tag_order_filename"))
            self.naming_rules = NamingRules()
            naming_rules_filename = Config.get_section_param(section_entries, "naming_rules_file")
            self.naming_rules.read_naming_rules(naming_rules_filename)
            self.past_tense_rules_obj = past_tense_rules.PastTenseRules()
            self.past_tense_rules_obj.read_past_tense_rules(
                Config.get_section_param(section_entries, "past_tense_rules_file"))
        else:
            self.auth_token = None

    def get_projects(self):
        response = requests.get(self.projects_endpoint, headers=self.headers)
        projects_list = response.json()
        projects_dict = {project['id']: project['name'] for project in projects_list}
        return projects_dict

    @staticmethod
    def toggl_entry_to_sectionstat(entry, projects_dict):
        project_name = "No project"
        if 'pid' in entry and entry['pid'] in projects_dict:
            project_name = projects_dict[entry['pid']]

        days = set()
        entry_date = datetime.strptime(entry['start'][:CHARACTERS_IN_DATE], '%Y-%m-%d').date()
        days.add(entry_date)
        entry_duration = entry['duration']
        unit_stats = UnitStats(done_pomodoros=(1 if MIN_POMODORO_IN_SECONDS < entry_duration < MAX_POMODORO_IN_SECONDS
                                               else 0))
        tags = set(entry['tags']) if 'tags' in entry else set()
        sectionstat = SectionStats(path=SECTIONSTAT_PATH_SEPARATOR.join([project_name, entry['description']]),
                                   seconds=entry_duration, tags=tags,
                                   days=days, unit_stats=unit_stats)
        return sectionstat

    @staticmethod
    def _diff_months(datetime1: datetime, datetime2: datetime):
        if datetime1 < datetime2:
            datetime1, datetime2 = datetime2, datetime1
        return (datetime1.year - datetime2.year) * 12 + datetime1.month - datetime2.month

    @staticmethod
    def _chunk_date_ranges(start, end) -> (datetime, datetime):
        num_chunks = TogglEntriesParser._diff_months(start, end) + 1
        diff = (end - start) / num_chunks
        range_start = start
        for i in range(1, num_chunks + 1):
            range_end = (start + diff * i)
            yield (range_start, range_end)
            range_start = range_end + timedelta(seconds=1)

    def get_section_stats(self, report_parameters, projects_dict):
        date_ranges = self._chunk_date_ranges(report_parameters.period_start, report_parameters.period_end)
        sectionstats_dict = {}
        for start_date, end_date in date_ranges:
            start_date_str = str(start_date).replace(" ", "T") + "Z"
            end_date_str = str(end_date).replace(" ", "T") + "Z"
            response = requests.get(self.entries_endpoint.format(start_date_str, end_date_str), headers=self.headers)
            entries_list = response.json()

            for entry in entries_list:
                sectionstat = self.toggl_entry_to_sectionstat(entry, projects_dict)
                if sectionstat.path in sectionstats_dict:
                    sectionstats_dict[sectionstat.path].add_stats(sectionstat)
                else:
                    sectionstats_dict[sectionstat.path] = sectionstat

        return sectionstats_dict

    def get_report_path(self, sectionstat):
        path = sectionstat.path.split(SECTIONSTAT_PATH_SEPARATOR)
        project_name = path[0]
        naming_rules_path = self.naming_rules.get_path(project_name)
        init_path = naming_rules_path.split(REPORT_PATH_SEPARATOR) if naming_rules_path else [project_name]
        leaf_name = self.past_tense_rules_obj.convert_to_past(path[1])
        tags_with_order = []
        for tag in sectionstat.common_tags:
            order = self.tag_order.get_order(tag)
            if order is not None:
                tags_with_order.append((tag.title(), order))
        ordered_meaningful_tags = [tag_and_order[0]
                                   for tag_and_order in sorted(tags_with_order, key=lambda x: (x[1], x[0]))]
        init_path.extend(ordered_meaningful_tags)
        if len(sectionstat.common_tags) != len(sectionstat.all_tags):
            init_path.append("Mixed")
        return init_path, leaf_name

    def extend_report(self, report, report_parameters):
        if not self.auth_token:
            pass

        projects = self.get_projects()
        event_stats_list = self.get_section_stats(report_parameters, projects)
        sorted_event_stats_list = sorted(event_stats_list.values(), key=lambda x: x.seconds, reverse=True)
        for event_stats in sorted_event_stats_list:
            init_path, leaf_name = self.get_report_path(event_stats)
            print(init_path, leaf_name)
            section = report.find_or_create_leaf(init_path, leaf_name)
            section.stats = event_stats
            Report.propagate_stats_to_parent(section, section.stats)


