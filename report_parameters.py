import datetime

from config import Config


class ReportParameters:

    def __init__(self, config_entries):
        super().__init__()
        self.year = Config.get_section_param(config_entries, 'report_year')
        self.week_number = Config.get_section_param(config_entries, 'report_week_number')
        self.week_start = datetime.datetime.combine(self.get_week_start(), datetime.datetime.min.time())
        self.week_end = datetime.datetime.combine(self.week_start +
                                                  datetime.timedelta(days=6), datetime.datetime.max.time())
        self.week_start_str = self.week_start.strftime("%d.%m")
        self.week_end_str = self.week_end.strftime("%d.%m")

        self.pic_dir = self.set_variables(Config.get_section_param(config_entries, 'pic_dir'))
        Config.make_dir(self.pic_dir)
        self.report_title = self.set_variables(Config.get_section_param(config_entries, 'report_title'))

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
