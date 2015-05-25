import configparser
import jiffycsvparser
import reporting
import htmlreport

naming_rules = {}

if __name__ == '__main__':
    config = configparser.RawConfigParser()
    config.read('generator.ini')
    jiffy_report = config['Files']['jiffy_report_file']

    jiffy_csv_parser = jiffycsvparser.JiffyCSVParser(config)
    jiffy_csv_parser.load_column_names()
    jiffy_csv_parser.load_file(jiffy_report)

    report = reporting.Report()
    report.create("Week", config['Files']['naming_rules_file'], jiffy_csv_parser.rows_stats_map)

    html_report = htmlreport.HtmlReport()
    html_report.generate(report, config['Files']['out_html_report_file'])

