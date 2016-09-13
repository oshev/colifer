import csv
from datetime import datetime

import sectionstats

ID_DIV = '-'
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class JiffyCSVParser:

    def __init__(self, config):
        super().__init__()
        self.column_name_project = ''
        self.column_name_task = ''
        self.column_name_extra = ''
        self.column_start_time = ''
        self.column_stop_time = ''
        self.rows_stats_map = {}
        self.config = config

    def load_column_names(self):
        self.column_name_project = self.config['Columns']['column_name_project']
        self.column_name_task = self.config['Columns']['column_name_task']
        self.column_start_time = self.config['Columns']['column_name_start_time']
        self.column_stop_time = self.config['Columns']['column_name_stop_time']
        self.column_name_extra = self.config['Columns']['column_name_extra']

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
            stat_object.jiffy_name = row_id
            self.rows_stats_map[row_id] = stat_object

        start_datetime = datetime.strptime(row[titles[self.column_start_time]], DATE_TIME_FORMAT)
        stop_datetime = datetime.strptime(row[titles[self.column_stop_time]], DATE_TIME_FORMAT)
        stat_object.seconds += round((stop_datetime - start_datetime).total_seconds())

        if row[titles[self.column_name_extra]].isdigit():
            stat_object.extra += int(row[titles[self.column_name_extra]])
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
