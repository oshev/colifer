import config
import constantparser
import htmlreport
import jiffycsvparser
import reporting
from articles import pocket_parser
from articles import zotero_parser
from trello.boardparser import TrelloBoardParser

if __name__ == '__main__':

    config = config.Config()

    jiffy_report = config.set_variables(config.get_param('Files.jiffy_report_file'))
    jiffy_csv_parser = jiffycsvparser.JiffyCSVParser(config)
    jiffy_csv_parser.load_column_names()
    jiffy_csv_parser.load_file(jiffy_report)

    report = reporting.Report()
    report.create(config.report_title)

    constant_parser = constantparser.ConstantParser()
    constant_parser.load_data(config.get_param('Files.constant_sections_file'), report)

    report.fill_jiffy_sections(config.get_param('Files.naming_rules_file'), jiffy_csv_parser.rows_stats_map)

    if config.get_param('Trello.stat_enabled'):
        trello_parser = TrelloBoardParser(config, report, config.pic_dir)
        trello_parser.load_data()

    pocket_parser = pocket_parser.PocketParser(config.get_param('Pocket.consumer_key'),
                                               config.get_param('Pocket.access_token'))
    pocket_parser.load_data(report, config.week_start, config.week_end, config.get_param('Pocket.naming_rules_file'))

    zotero_parser = zotero_parser.ZoteroParser(config.get_param('Zotero.library_id'),
                                               config.get_param('Zotero.library_type'),
                                               config.get_param('Zotero.api_key'),
                                               config.get_param('Zotero.read_tag'))
    zotero_parser.load_data(report, config.week_start, config.week_end, config.get_param('Zotero.naming_rules_file'))

    html_report = htmlreport.HtmlReport()
    out_html_report_file = config.set_variables(config.get_param('Files.out_html_report_file'))
    html_report.generate(report, out_html_report_file,
                         config.get_param('Html.before_report'),
                         config.get_param('Html.after_report'))

