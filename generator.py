import configparser
import jiffycsvparser
import reporting
import htmlreport
import trelloparser
import constantparser

naming_rules = {}

if __name__ == '__main__':
    config = configparser.RawConfigParser()
    config.read('generator.ini')
    jiffy_report = config['Files']['jiffy_report_file']

    jiffy_csv_parser = jiffycsvparser.JiffyCSVParser(config)
    jiffy_csv_parser.load_column_names()
    jiffy_csv_parser.load_file(jiffy_report)

    report = reporting.Report()
    report.create(config['ReportSpecific']['report_title'])

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

    html_report = htmlreport.HtmlReport()
    html_report.generate(report, config['Files']['out_html_report_file'],
                         config['Html']['before_report'],
                         config['Html']['after_report'])

