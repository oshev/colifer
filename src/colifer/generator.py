import argparse

from colifer.markdown_report import MarkdownReport
from colifer.reporting import Report
from colifer.config import Config
from colifer.report_parameters import ReportParameters
from colifer.reportextenders.articles.pocket_parser import PocketParser
from colifer.reportextenders.articles.zotero_parser import ZoteroParser
from colifer.reportextenders.constant_parser import ConstantParser
from colifer.reportextenders.toggl import TogglEntriesParser

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", required=True,
                        help="The year for which report should be generated", type=int)
    parser.add_argument("--type", required=True,
                        help="Report type (yearly, quarterly, monthly, weekly)", type=str)
    parser.add_argument("--period-num", required=True,
                        help="The number of the period: quarter (1-4), month (1-12), "
                             "or week (1-53); depending on the report type", type=int)

    args = parser.parse_args()

    config = Config()
    report_parameters = ReportParameters(config.get_param("Report"), args.type, args.year,
                                         args.period_num)

    extenders = [
        ConstantParser(config.get_param("ConstantSection")),
        TogglEntriesParser(config.get_param('Toggl')),
        PocketParser(config.get_param('Pocket')),
        ZoteroParser(config.get_param('Zotero')),
    ]

    report = Report()
    report.create(report_parameters.report_title)

    for extender in extenders:
        extender.extend_report(report, report_parameters)

    md_report = MarkdownReport()
    md_config_entries = config.get_param('MarkdownGenerator')
    out_md_report_file = report_parameters.set_variables(
        Config.get_section_param(md_config_entries, 'out_md_report_file'))
    md_report.generate(report, out_md_report_file,
                       Config.get_section_param(md_config_entries, 'before_report'),
                       Config.get_section_param(md_config_entries, 'after_report'))
