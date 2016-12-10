import csv
from datetime import datetime

import sectionstats
from config import Config
from reportextenders.report_extender import ReportExtender
from reporting import Report

ID_DIV = '-'
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
SECTION_SEPARATOR = '/'


class JiffyCSVParser(ReportExtender):

    def __init__(self, section_entries):
        super().__init__(section_entries)
        if Config.get_section_param(section_entries, "enabled"):
            self.enabled = True
            self.column_name_project = ''
            self.column_name_task = ''
            self.column_name_extra = ''
            self.column_start_time = ''
            self.column_stop_time = ''
            self.rows_stats_map = {}
            self.column_name_project = Config.get_section_param(section_entries, 'column_name_project')
            self.column_name_task = Config.get_section_param(section_entries, 'column_name_task')
            self.column_start_time = Config.get_section_param(section_entries, 'column_name_start_time')
            self.column_stop_time = Config.get_section_param(section_entries, 'column_name_stop_time')
            self.column_name_extra = Config.get_section_param(section_entries, 'column_name_extra')
            self.jiffy_report_filename_template = Config.get_section_param(section_entries, 'report_file')
            self.naming_rules_filename = Config.get_section_param(section_entries, 'naming_rules_file')
        else:
            self.enabled = False

    def extend_report(self, report, report_parameters):
        if self.enabled:
            jiffy_report_name = report_parameters.set_variables(self.jiffy_report_filename_template)
            self.load_file(jiffy_report_name)

            lines = [line.strip() for line in open(self.naming_rules_filename)]
            for row in lines:
                if row != '' and not row.startswith('#'):
                    elements = row.split('=')
                    if len(elements) == 2:
                        jiffy_id = elements[0]
                        section_path_elements = elements[1].split(SECTION_SEPARATOR)
                        if jiffy_id in self.rows_stats_map.keys():
                            section = report.find_or_create_section(report.root_section, section_path_elements, True)
                            section.stats = self.rows_stats_map[jiffy_id]
                            Report.propagate_stats_to_parent(section, section.stats)

    def check_titles(self, titles):
        if titles[self.column_name_project] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_project + ' in CSV')
        if titles[self.column_name_task] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_task + ' in CSV')
        if titles[self.column_start_time] is None:
            raise NameError('Can\'t find necessary column ' + self.column_start_time + ' in CSV')
        if titles[self.column_stop_time] is None:
            raise NameError('Can\'t find necessary column ' + self.column_stop_time + ' in CSV')
        if titles[self.column_name_extra] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_extra + ' in CSV')

    def update_stat_object(self, row_id, row, titles):
        if row_id in self.rows_stats_map.keys():
            stat_object = self.rows_stats_map[row_id]
        else:
            stat_object = sectionstats.SectionStats()
            stat_object.path = row_id
            self.rows_stats_map[row_id] = stat_object

        start_datetime = datetime.strptime(row[titles[self.column_start_time]], DATE_TIME_FORMAT)
        stop_datetime = datetime.strptime(row[titles[self.column_stop_time]], DATE_TIME_FORMAT)
        stat_object.seconds += round((stop_datetime - start_datetime).total_seconds())

        if row[titles[self.column_name_extra]].isdigit():
            stat_object.words_num += int(row[titles[self.column_name_extra]])
        elif row[titles[self.column_name_extra]] != '':
            stat_object.comments_list.append(row[titles[self.column_name_extra]])

    def load_file(self, filename):
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            titles = {}
            for row in reader:
                if len(titles) == 0:
                    index = 0
                    for col in row:
                        titles[col] = index
                        index += 1
                    self.check_titles(titles)
                else:
                    if row[titles[self.column_name_task]] == '':
                        row_id = row[titles[self.column_name_project]]
                    else:
                        row_id = row[titles[self.column_name_project]] + ID_DIV + row[titles[self.column_name_task]]

                    self.update_stat_object(row_id, row, titles)

            # print(self.rows_stats_map)
