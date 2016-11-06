import htmlreport
import reporting
from config import Config
from report_parameters import ReportParameters
from reportextenders.articles.pocket_parser import PocketParser
from reportextenders.articles.zotero_parser import ZoteroParser
from reportextenders.constant_parser import ConstantParser
from reportextenders.jiffy_csv_parser import JiffyCSVParser
from reportextenders.trello.boardparser import TrelloBoardParser

if __name__ == '__main__':

    config = Config()
    report_parameters = ReportParameters(config.get_param("Report"))

    extenders = [
        ConstantParser(config.get_param("ConstantSection")),
        JiffyCSVParser(config.get_param('Jiffy')),
        TrelloBoardParser(config.get_param('Trello')),
        PocketParser(config.get_param('Pocket')),
        ZoteroParser(config.get_param('Zotero'))
    ]

    report = reporting.Report()
    report.create(report_parameters.report_title)

    for extender in extenders:
        extender.extend_report(report, report_parameters)

    html_report = htmlreport.HtmlReport()
    html_config_entries = config.get_param('HtmlGenerator')
    out_html_report_file = report_parameters.set_variables(
        Config.get_section_param(html_config_entries, 'out_html_report_file'))
    html_report.generate(report, out_html_report_file,
                         Config.get_section_param(html_config_entries, 'before_report'),
                         Config.get_section_param(html_config_entries, 'after_report'))

