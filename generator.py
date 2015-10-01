import configparser
import jiffycsvparser
import reporting
import htmlreport
import trelloparser
import constantparser
import pocketparser
import datetime

def get_week_start(year, week_number):
    date = datetime.date(int(year), 1, 1)
    date_end = datetime.date(int(year) + 1, 1, 7)
    while date < date_end:
        if date.isocalendar()[1] == int(week_number):
            return date
        date = date + datetime.timedelta(days=1)

def set_variables(str, year, week_number, week_start_str, week_end_str):
    return str.replace('%REPORT_YEAR', year).\
        replace('%WEEK_NUMBER', week_number).\
        replace('%WEEK_START', week_start_str).\
        replace('%WEEK_END', week_end_str)

if __name__ == '__main__':
    config = configparser.RawConfigParser()
    config.read('configs/generator.ini')

    year = config['ReportSpecific']['report_year']
    week_number = config['ReportSpecific']['report_week_number']
    week_start = datetime.datetime.combine(get_week_start(year, week_number), datetime.datetime.min.time())
    week_end = datetime.datetime.combine(week_start + datetime.timedelta(days=6), datetime.datetime.max.time())
    week_start_str = week_start.strftime("%d.%m")
    week_end_str = week_end.strftime("%d.%m")

    jiffy_report = set_variables(config['Files']['jiffy_report_file'],
                                 year, week_number, week_start_str, week_end_str)
    jiffy_csv_parser = jiffycsvparser.JiffyCSVParser(config)
    jiffy_csv_parser.load_column_names()
    jiffy_csv_parser.load_file(jiffy_report)

    report = reporting.Report()
    report.create(set_variables(config['ReportSpecific']['report_title'],
                                year, week_number, week_start_str, week_end_str))

    constant_parser = constantparser.ConstantParser()
    constant_parser.load_data(config['Files']['constant_sections_file'], report)

    report.fill_jiffy_sections(config['Files']['naming_rules_file'], jiffy_csv_parser.rows_stats_map)

    if config['Trello']['trello_stat_enabled'] == 'true':
        trello_parser = trelloparser.TrelloParser(config['Trello']['trello_api_key'],
                                                  config['Trello']['trello_user_oauth_token'])
        trello_parser.load_data(config['Trello']['trello_board_id'],
                                config['Trello']['trello_list_done_name'],
                                config['Trello']['trello_list_failed_name'],
                                config['Trello']['trello_list_notes_name'],
                                config['Trello']['naming_rules_file'],
                                report)

    pocket_parser = pocketparser.PocketParser(config['Pocket']['consumer_key'], config['Pocket']['access_token'])
    pocket_parser.load_data(report, week_start, week_end, config['Pocket']['naming_rules_file'])

    html_report = htmlreport.HtmlReport()
    out_html_report_file = set_variables(config['Files']['out_html_report_file'],
                                         year, week_number, week_start_str, week_end_str)
    html_report.generate(report, out_html_report_file,
                         config['Html']['before_report'],
                         config['Html']['after_report'])

