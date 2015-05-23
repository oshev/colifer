import configparser
import jiffycsvparser
import reporting

naming_rules = {}

if __name__ == '__main__':
    config = configparser.RawConfigParser()
    config.read('reportgenerator.ini')
    jiffy_report = config['Main']['jiffy_report_file']

    jiffy_csv_parser = jiffycsvparser.JiffyCSVParser(config)
    jiffy_csv_parser.load_column_names()
    jiffy_csv_parser.load_file(jiffy_report)

    report = reporting.Report()
    report.create("Week", config['Main']['naming_rules_file'], jiffy_csv_parser.rows_stats_map)
    print(report)

