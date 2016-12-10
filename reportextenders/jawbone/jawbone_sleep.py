from collections import OrderedDict
from datetime import datetime

import requests

from config import Config
from namingrules import NamingRules
from reportextenders.graphs import Graphs
from reportextenders.report_extender import ReportExtender

SECTION_SEPARATOR = '/'

SLEEP_LIGHT_NAME = "Light"
SLEEP_DEEP_NAME = "Deep"
SLEEP_REM_NAME = "REM"
SLEEP_AWAKE_NAME = "Awake"
SLEEP_TOTAL_NAME = "Total"
SLEEP_NOT_AWAKE = "Not Awake"
SLEEP_START = "Asleep hour"
SLEEP_END = "Awake hour"

SLEEP_NAMING_RULE = "Sleep"
MOVES_NAMING_RULE = "Moves"


class Measure:
    def __init__(self, color):
        self.color = color
        self.values = []


class JawboneSleepParser(ReportExtender):
    def __init__(self, section_entries):
        super().__init__(section_entries)
        if Config.get_section_param(section_entries, "enabled"):
            self.auth_token = Config.get_section_param(section_entries, "auth_token")
            self.graph_tag = Config.get_section_param(section_entries, 'graph_tag')
            self.headers = {'Authorization': 'Bearer ' + self.auth_token}
            self.end_point = Config.get_section_param(section_entries, "endpoint")
            self.sleep_by_days_graph_filename = Config.get_section_param(section_entries, "sleep_by_days_graph_file")
            self.asleep_by_days_graph_filename = Config.get_section_param(section_entries, "asleep_by_days_graph_file")
            self.naming_rules = NamingRules()
            naming_rules_filename = Config.get_section_param(section_entries, "naming_rules_file")
            self.naming_rules.read_naming_rules(naming_rules_filename)
            self.sleep_stats_path = self.naming_rules.get_path(SLEEP_NAMING_RULE)
        else:
            self.auth_token = None

    @staticmethod
    def init_measures():
        measures = OrderedDict()
        measures[SLEEP_LIGHT_NAME] = Measure('y')
        measures[SLEEP_DEEP_NAME] = Measure('b')
        measures[SLEEP_REM_NAME] = Measure('c')
        measures[SLEEP_AWAKE_NAME] = Measure('g')
        measures[SLEEP_TOTAL_NAME] = Measure('k')
        measures[SLEEP_NOT_AWAKE] = Measure('r')
        return measures

    @staticmethod
    def init_measures_hour():
        measures_hour = OrderedDict()
        measures_hour[SLEEP_START] = Measure('b')
        measures_hour[SLEEP_END] = Measure('r')
        return measures_hour

    def add_sleep_by_days_stats(self, report, report_parameters, sleep_stats_path_elements, measures, days):
        full_img_path = report_parameters.pic_dir + "/" + self.sleep_by_days_graph_filename
        relative_img_path = report_parameters.pic_dir.split('/')[-1] + "/" + self.sleep_by_days_graph_filename
        Graphs.save_line_graph(full_img_path, 'Sleep statistics by days',
                               measures, days, 'Hours', y_min=0, y_max=11)
        report.find_or_create_leaf(sleep_stats_path_elements, self.graph_tag.format(relative_img_path).strip())

    def add_awake_asleep_by_days_stats(self, report, report_parameters, sleep_stats_path_elements, measures, days):
        full_img_path = report_parameters.pic_dir + "/" + self.asleep_by_days_graph_filename
        relative_img_path = report_parameters.pic_dir.split('/')[-1] + "/" + self.asleep_by_days_graph_filename
        Graphs.save_line_graph(full_img_path, 'Asleep / Awake statistics by days',
                               measures, days, 'Hours', y_min=-3, y_max=12)
        report.find_or_create_leaf(sleep_stats_path_elements, self.graph_tag.format(relative_img_path).strip())

    def extend_report(self, report, report_parameters):
        if not self.auth_token:
            pass
        if not self.sleep_stats_path:
            print("You must add Sleep report path to JawBone naming rules file")
            exit(1)

        measures = self.init_measures()
        measures_hour = self.init_measures_hour()

        response = requests.get(self.end_point.format(report_parameters.week_start.timestamp(),
                                                      report_parameters.week_end.timestamp()),
                                headers=self.headers)
        data = response.json()
        days = []
        sleep_week_minutes = 0
        sleep_week_minutes_not_awake = 0
        sleep_week_awakenings = 0
        for item in data["data"]["items"][:7]:
            sleep_date = datetime.strptime(str(item['date']), '%Y%m%d')
            awakenings_num = self.safe_get(item['details'], 'awakenings', 0)
            sleep_start = datetime.fromtimestamp(item['details']['asleep_time'])
            sleep_end = datetime.fromtimestamp(item['details']['awake_time'])

            sleep_light_minutes = self.safe_get(item['details'], 'light', 0) / 60
            sleep_rem_minutes = self.safe_get(item['details'], 'rem', 0) / 60
            sleep_awake_minutes = self.safe_get(item['details'], 'awake', 0) / 60
            sleep_total_minutes = self.safe_get(item['details'], 'duration', 0) / 60
            sleep_not_awake_minutes = sleep_total_minutes - sleep_awake_minutes
            sleep_deep_minutes = sleep_total_minutes - sleep_light_minutes - sleep_rem_minutes - sleep_awake_minutes

            sleep_week_minutes += sleep_total_minutes
            sleep_week_minutes_not_awake += sleep_not_awake_minutes
            sleep_week_awakenings += awakenings_num

            days.append(sleep_date.strftime("%a %d/%m"))
            measures[SLEEP_LIGHT_NAME].values.append(round(sleep_light_minutes / 60, 2))
            measures[SLEEP_DEEP_NAME].values.append(round(sleep_deep_minutes / 60, 2))
            measures[SLEEP_REM_NAME].values.append(round(sleep_rem_minutes / 60, 2))
            measures[SLEEP_AWAKE_NAME].values.append(round(sleep_awake_minutes / 60, 2))
            measures[SLEEP_TOTAL_NAME].values.append(round(sleep_total_minutes / 60, 2))
            measures[SLEEP_NOT_AWAKE].values.append(round(sleep_not_awake_minutes / 60, 2))

            sleep_start_hour = (sleep_start.hour - 24
                                if sleep_start.hour > 15
                                else sleep_start.hour) + sleep_start.minute / 60
            sleep_end_hour = sleep_end.hour + sleep_end.minute / 60
            measures_hour[SLEEP_START].values.append(sleep_start_hour)
            measures_hour[SLEEP_END].values.append(sleep_end_hour)

        sleep_week_minutes = round(sleep_week_minutes)
        sleep_week_minutes_not_awake = round(sleep_week_minutes_not_awake)
        sleep_stats_path_elements = self.sleep_stats_path.split(SECTION_SEPARATOR)

        total_sleep_stats_path_elements = sleep_stats_path_elements.copy()
        total_sleep_stats_path_elements.append("Total")
        report.find_or_create_leaf(total_sleep_stats_path_elements,
                                   "Sleep time: {}:{}".format(sleep_week_minutes // 60,
                                                                    str(sleep_week_minutes % 60).zfill(2)))
        report.find_or_create_leaf(total_sleep_stats_path_elements,
                                   "Quality sleep time: {}:{}".format(sleep_week_minutes_not_awake // 60,
                                                                            str(sleep_week_minutes_not_awake %
                                                                                60).zfill(2)))
        sleep_week_minutes_awake = sleep_week_minutes - sleep_week_minutes_not_awake
        report.find_or_create_leaf(total_sleep_stats_path_elements,
                                   "Awake time: {}:{}".format(sleep_week_minutes_awake // 60,
                                                                    str(sleep_week_minutes_awake % 60).zfill(2)))

        average_sleep_stats_path_elements = sleep_stats_path_elements.copy()
        average_sleep_stats_path_elements.append("Average per day/night")
        avg_awakenings_per_night = round(sleep_week_awakenings / len(days), 2)
        report.find_or_create_leaf(average_sleep_stats_path_elements, "Awakenings: {}".format(avg_awakenings_per_night))
        avg_sleep_per_day = sleep_week_minutes_not_awake // len(days)
        report.find_or_create_leaf(average_sleep_stats_path_elements,
                                   "Sleep: {}:{}".format(avg_sleep_per_day // 60, str(avg_sleep_per_day % 60).zfill(2)))

        report.find_or_create_leaf(sleep_stats_path_elements, "Sleep efficiency: {}%".
                                   format(round((sleep_week_minutes - sleep_week_minutes_awake) /
                                                sleep_week_minutes * 100)))

        self.add_sleep_by_days_stats(report, report_parameters, sleep_stats_path_elements, measures, days)

        self.add_awake_asleep_by_days_stats(report, report_parameters, sleep_stats_path_elements, measures_hour, days)

