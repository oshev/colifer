import datetime
import errno
import os

import yaml


class Config:

    def __init__(self):
        super().__init__()
        config_yaml_stream = open('configs/colifer.yaml', "r")
        self.entries = yaml.load(config_yaml_stream)

        self.year = self.get_param('ReportSpecific.report_year')
        self.week_number = self.get_param('ReportSpecific.report_week_number')
        self.week_start = datetime.datetime.combine(self.get_week_start(), datetime.datetime.min.time())
        self.week_end = datetime.datetime.combine(self.week_start +
                                                  datetime.timedelta(days=6), datetime.datetime.max.time())
        self.week_start_str = self.week_start.strftime("%d.%m")
        self.week_end_str = self.week_end.strftime("%d.%m")

        self.pic_dir = self.set_variables(self.get_param('Files.pic_dir'))
        self.make_dir(self.pic_dir)
        self.report_title = self.set_variables(self.get_param('ReportSpecific.report_title'))

    @staticmethod
    def get_config_recursive(entry, elements):
        if len(elements) > 0 and type(entry) is dict:
            return Config.get_config_recursive(entry[elements[0]], elements[1:])
        else:
            return entry

    def get_param(self, path):
        elements = path.split('.')
        return Config.get_config_recursive(self.entries, elements)

    def get_week_start(self):
        date = datetime.date(int(self.year), 1, 1)
        date_end = datetime.date(int(self.year) + 1, 1, 7)
        while date < date_end:
            if date.isocalendar()[1] == int(self.week_number):
                return date
            date += datetime.timedelta(days=1)

    def set_variables(self, string):
        return string.replace('%REPORT_YEAR', str(self.year)).\
            replace('%WEEK_NUMBER', str(self.week_number)).\
            replace('%WEEK_START', self.week_start_str).\
            replace('%WEEK_END', self.week_end_str)

    @staticmethod
    def make_dir(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
