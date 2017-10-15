import datetime
import calendar
from config import Config
from enum import Enum


class ReportType(Enum):
    YEARLY = 'yearly'
    QUARTERLY = 'quarterly'
    MONTHLY = 'monthly'
    WEEKLY = 'weekly'


class ReportParameters:

    def __init__(self, config_entries, report_type_name: str, year: int, period_num: int):
        super().__init__()

        report_type_values = [item.value for item in ReportType]
        report_type = None
        if report_type_name.lower() not in report_type_values:
            print("Non-existent report type {}, supported types: {}".format(report_type_name, report_type_values))
            exit(1)
        else:
            report_type = ReportType(report_type_name.lower())

        self.period_number = period_num
        self.year = year
        if report_type == ReportType.YEARLY:
            self.period_type = "Year"
            self.period_value = str(self.period_number)
            self.period_start, self.period_end = self._get_year_start_end(self.year)
        elif report_type == ReportType.QUARTERLY:
            self._abort_if_period_invalid(period_num, 1, 4, "quarter")
            self.period_type = "Quarter"
            self.period_value = str(self.period_number)
            self.period_start, self.period_end = self._get_quarter_start_end(self.year, self.period_number)
        elif report_type == ReportType.MONTHLY:
            self._abort_if_period_invalid(period_num, 1, 12, "month")
            self.period_type = "Month"
            month_name = datetime.date(year, self.period_number, 1).strftime('%B')
            self.period_value = str(self.period_number) + " ({})".format(month_name)
            self.period_start, self.period_end = self._get_month_start_end(self.year, self.period_number)
        elif report_type == ReportType.WEEKLY:
            self._abort_if_period_invalid(period_num, 1, 52, "week")
            self.period_value = str(self.period_number)
            self.period_type = "Week"
            self.period_start, self.period_end = self._get_week_start_end(self.year, self.period_number)

        self.period_start_str = self.period_start.strftime("%d.%m")
        self.period_end_str = self.period_end.strftime("%d.%m")
        self.report_title = self.set_variables(Config.get_section_param(config_entries, 'report_title'))

        self.pic_dir = self.set_variables(Config.get_section_param(config_entries, 'pic_dir'))
        Config.make_dir(self.pic_dir)

    @staticmethod
    def _abort_if_period_invalid(period_number: int, min_value: int, max_value: int, period_name: str):
        if max_value > period_number < min_value:
            print("Wrong {} number, accepted values {}-{}.".format(period_name, min_value, max_value))
            exit(1)

    @staticmethod
    def _get_year_start_end(year: int) -> (datetime.datetime, datetime.datetime):
        datetime_start = datetime.datetime.combine(datetime.date(year, 1, 1), datetime.datetime.min.time())
        datetime_end = datetime.datetime.combine(datetime.date(year, 12, 31), datetime.datetime.max.time())
        return datetime_start, datetime_end

    @staticmethod
    def _get_quarter_start_end(year: int, quarter: int) -> (datetime.datetime, datetime.datetime):
        first_month_of_quarter = 3 * quarter - 2
        last_month_of_quarter = 3 * quarter
        date_of_first_day_of_quarter = datetime.date(year, first_month_of_quarter, 1)
        date_of_last_day_of_quarter = datetime.date(year, last_month_of_quarter,
                                                    calendar.monthrange(year, last_month_of_quarter)[1])
        datetime_start = datetime.datetime.combine(date_of_first_day_of_quarter, datetime.datetime.min.time())
        datetime_end = datetime.datetime.combine(date_of_last_day_of_quarter, datetime.datetime.max.time())
        return datetime_start, datetime_end

    @staticmethod
    def _get_month_start_end(year: int, month: int) -> (datetime.datetime, datetime.datetime):
        month_end_date = calendar.monthrange(year, month)[1]
        datetime_start = datetime.datetime.combine(datetime.date(year, month, 1), datetime.datetime.min.time())
        datetime_end = datetime.datetime.combine(datetime.date(year, month, month_end_date),
                                                 datetime.datetime.max.time())
        return datetime_start, datetime_end

    @staticmethod
    def _get_week_start_end(year: int, week: int) -> (datetime.datetime, datetime.datetime):
        date = datetime.date(int(year), 1, 1)
        date_end = datetime.date(int(year) + 1, 1, 7)
        while date < date_end:
            if date.isocalendar()[1] == week:
                break
            date += datetime.timedelta(days=1)
        datetime_start = datetime.datetime.combine(date, datetime.datetime.min.time())
        datetime_end = datetime.datetime.combine(datetime_start.date() + datetime.timedelta(days=6),
                                                 datetime.datetime.max.time())
        return datetime_start, datetime_end

    def set_variables(self, string):
        return string.replace('%REPORT_YEAR', str(self.year)). \
            replace('%PERIOD_TYPE', str(self.period_type)). \
            replace('%PERIOD_VALUE', " {}".format(self.period_value)).\
            replace('%PERIOD_START', self.period_start_str).\
            replace('%PERIOD_END', self.period_end_str)
