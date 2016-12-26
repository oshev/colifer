from collections import OrderedDict
from datetime import datetime

import requests

from config import Config
from namingrules import NamingRules
from reportextenders.graphs import Graphs
from reportextenders.report_extender import ReportExtender
import numpy as np

SECTION_SEPARATOR = '/'

STEPS_NAME = "Steps"
METERS_NAME = "Meters"
ACTIVE_NAME = "Active"
INACTIVE_NAME = "Inactive"
IDLE_NAME = "Longest idle"

MOVES_NAMING_RULE = "Moves"


class Measure:
    def __init__(self, color):
        self.color = color
        self.values = []


class JawboneMovesParser(ReportExtender):
    def __init__(self, section_entries):
        super().__init__(section_entries)
        if Config.get_section_param(section_entries, "enabled"):
            self.auth_token = Config.get_section_param(section_entries, "auth_token")
            self.graph_tag = Config.get_section_param(section_entries, 'graph_tag')
            self.headers = {'Authorization': 'Bearer ' + self.auth_token}
            self.end_point = Config.get_section_param(section_entries, "endpoint")
            self.steps_by_days_graph_filename = Config.get_section_param(section_entries, "steps_by_days_graph_file")
            self.activity_by_days_graph_filename = Config.get_section_param(section_entries,
                                                                            "activity_by_days_graph_file")
            self.naming_rules = NamingRules()
            naming_rules_filename = Config.get_section_param(section_entries, "naming_rules_file")
            self.naming_rules.read_naming_rules(naming_rules_filename)
            self.moves_stats_path = self.naming_rules.get_path(MOVES_NAMING_RULE)
        else:
            self.auth_token = None

    @staticmethod
    def init_measures_steps():
        measures = OrderedDict()
        measures[STEPS_NAME] = Measure('b')
        measures[METERS_NAME] = Measure('r')
        return measures

    @staticmethod
    def init_measures_time():
        measures_minutes = OrderedDict()
        measures_minutes[INACTIVE_NAME] = Measure('b')
        measures_minutes[ACTIVE_NAME] = Measure('r')
        measures_minutes[IDLE_NAME] = Measure('c')
        return measures_minutes

    def add_steps_by_days_stats(self, report, report_parameters, moves_stats_path_elements, measures, days):
        full_img_path = report_parameters.pic_dir + "/" + self.steps_by_days_graph_filename
        relative_img_path = report_parameters.pic_dir.split('/')[-1] + "/" + self.steps_by_days_graph_filename
        Graphs.save_line_graph(full_img_path, 'Walk statistics by days',
                               measures, days, 'Steps / Meters', y_min=0, y_max=30000, y_tick_step=2000)
        report.find_or_create_leaf(moves_stats_path_elements, self.graph_tag.format(relative_img_path).strip())

    def add_activity_by_days_stats(self, report, report_parameters, moves_stats_path_elements, measures, days):
        full_img_path = report_parameters.pic_dir + "/" + self.activity_by_days_graph_filename
        relative_img_path = report_parameters.pic_dir.split('/')[-1] + "/" + self.activity_by_days_graph_filename
        measures_hour = self.init_measures_time()
        for measure_key in measures_hour.keys():
            measure = measures[measure_key]
            measures_hour[measure_key].values = [value/60 for value in measure.values]
        Graphs.save_line_graph(full_img_path, 'Activity statistics by days',
                               measures_hour, days, 'Hours', y_min=0, y_max=24)
        report.find_or_create_leaf(moves_stats_path_elements, self.graph_tag.format(relative_img_path).strip())

    def extend_report(self, report, report_parameters):
        if not self.auth_token:
            return
        if not self.moves_stats_path:
            print("You must add Moves report path to JawBone naming rules file")
            exit(1)

        measures_steps = self.init_measures_steps()
        measures_minutes = self.init_measures_time()
        response = requests.get(self.end_point.format(report_parameters.week_start.timestamp(),
                                                      report_parameters.week_end.timestamp()), headers=self.headers)
        data = response.json()
        days = []
        calories_all = []
        for item in data["data"]["items"][:7]:
            move_date = datetime.strptime(str(item['date']), '%Y%m%d')
            steps = self.safe_get(item['details'], 'steps', 0)
            meters = self.safe_get(item['details'], 'distance', 0)
            active_minutes = self.safe_get(item['details'], 'active_time', 0) / 60
            inactive_minutes = self.safe_get(item['details'], 'inactive_time', 0) / 60
            calories = self.safe_get(item['details'], 'calories', 0)
            longest_idle = self.safe_get(item['details'], 'longest_idle', 0) / 60

            days.append(move_date.strftime("%a %d/%m"))
            measures_steps[STEPS_NAME].values.append(steps)
            measures_steps[METERS_NAME].values.append(meters)
            measures_minutes[ACTIVE_NAME].values.append(active_minutes)
            measures_minutes[INACTIVE_NAME].values.append(inactive_minutes)
            measures_minutes[IDLE_NAME].values.append(longest_idle)
            calories_all.append(calories)

        moves_stats_path_elements = self.moves_stats_path.split(SECTION_SEPARATOR)
        total_moves_stats_path_elements = moves_stats_path_elements.copy()
        total_moves_stats_path_elements.append("Total")
        report.find_or_create_leaf(total_moves_stats_path_elements,
                                   "Steps: {}".format(sum(measures_steps[STEPS_NAME].values)))
        report.find_or_create_leaf(total_moves_stats_path_elements,
                                   "Meters: {}".format(round(sum(measures_steps[METERS_NAME].values))))
        report.find_or_create_leaf(total_moves_stats_path_elements,
                                   "Calories burned: {}".format(round(sum(calories_all))))
        report.find_or_create_leaf(total_moves_stats_path_elements,
                                   "Active time: {}:{}".
                                   format(str(round(sum(measures_minutes[ACTIVE_NAME].values) / 60)).zfill(2),
                                          str(round(sum(measures_minutes[ACTIVE_NAME].values) % 60)).zfill(2)))
        report.find_or_create_leaf(total_moves_stats_path_elements,
                                   "Inactive time: {}:{}".
                                   format(str(round(sum(measures_minutes[INACTIVE_NAME].values) / 60)).zfill(2),
                                          str(round(sum(measures_minutes[INACTIVE_NAME].values) % 60)).zfill(2)))

        avg_moves_stats_path_elements = moves_stats_path_elements.copy()
        avg_moves_stats_path_elements.append("Average per day")
        report.find_or_create_leaf(avg_moves_stats_path_elements,
                                   "Steps: {}".format(int(np.mean(measures_steps[STEPS_NAME].values))))
        report.find_or_create_leaf(avg_moves_stats_path_elements,
                                   "Meters: {}".format(int(np.mean(measures_steps[METERS_NAME].values))))
        report.find_or_create_leaf(avg_moves_stats_path_elements,
                                   "Calories burned: {}".format(int(np.mean(calories_all))))
        avg_active_minutes = int(round(np.mean(measures_minutes[ACTIVE_NAME].values)))
        report.find_or_create_leaf(avg_moves_stats_path_elements,
                                   "Active time: {}:{}".format(str(round(avg_active_minutes / 60)).zfill(2),
                                                               str(round(avg_active_minutes % 60)).zfill(2)))
        avg_inactive_minutes = int(round(np.mean(measures_minutes[INACTIVE_NAME].values)))
        report.find_or_create_leaf(avg_moves_stats_path_elements,
                                   "Inactive time: {}:{}".format(str(round(avg_inactive_minutes / 60)).zfill(2),
                                                                 str(round(avg_inactive_minutes % 60)).zfill(2)))
        avg_longest_idle_minutes = int(round(np.mean(measures_minutes[IDLE_NAME].values)))
        report.find_or_create_leaf(avg_moves_stats_path_elements,
                                   "Longest idle: {}:{}".format(str(round(avg_longest_idle_minutes / 60)).zfill(2),
                                                                str(round(avg_longest_idle_minutes % 60)).zfill(2)))

        self.add_steps_by_days_stats(report, report_parameters, moves_stats_path_elements, measures_steps, days)

        self.add_activity_by_days_stats(report, report_parameters, moves_stats_path_elements, measures_minutes, days)
