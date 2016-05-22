import datetime
import errno
import os

import configparser
from trello.parser import TrelloParser

import constantparser
import htmlreport
import jiffycsvparser
import pocketparser
import reporting

config = configparser.RawConfigParser()


def get_week_start():
    date = datetime.date(int(year), 1, 1)
    date_end = datetime.date(int(year) + 1, 1, 7)
    while date < date_end:
        if date.isocalendar()[1] == int(week_number):
            return date
        date += datetime.timedelta(days=1)


def set_variables(string):
    return string.replace('%REPORT_YEAR', year).\
        replace('%WEEK_NUMBER', week_number).\
        replace('%WEEK_START', week_start_str).\
        replace('%WEEK_END', week_end_str)


def make_dir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

if __name__ == '__main__':
    config.read('configs/generator.ini')

    year = config['ReportSpecific']['report_year']
    week_number = config['ReportSpecific']['report_week_number']
    week_start = datetime.datetime.combine(get_week_start(), datetime.datetime.min.time())
    week_end = datetime.datetime.combine(week_start + datetime.timedelta(days=6), datetime.datetime.max.time())
    week_start_str = week_start.strftime("%d.%m")
    week_end_str = week_end.strftime("%d.%m")

    pic_dir = set_variables(config['Files']['pic_dir'])
    make_dir(pic_dir)

    jiffy_report = set_variables(config['Files']['jiffy_report_file'])
    jiffy_csv_parser = jiffycsvparser.JiffyCSVParser(config)
    jiffy_csv_parser.load_column_names()
    jiffy_csv_parser.load_file(jiffy_report)

    report = reporting.Report()
    report.create(set_variables(config['ReportSpecific']['report_title']))

    constant_parser = constantparser.ConstantParser()
    constant_parser.load_data(config['Files']['constant_sections_file'], report)

    report.fill_jiffy_sections(config['Files']['naming_rules_file'], jiffy_csv_parser.rows_stats_map)

    if config['Trello']['stat_enabled'] == 'true':
        trello_parser = TrelloParser(config['Trello'], report, pic_dir)
        trello_parser.load_data()

    pocket_parser = pocketparser.PocketParser(config['Pocket']['consumer_key'], config['Pocket']['access_token'])
    pocket_parser.load_data(report, week_start, week_end, config['Pocket']['naming_rules_file'])

    html_report = htmlreport.HtmlReport()
    out_html_report_file = set_variables(config['Files']['out_html_report_file'])
    html_report.generate(report, out_html_report_file,
                         config['Html']['before_report'],
                         config['Html']['after_report'])

