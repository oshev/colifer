from datetime import datetime

from pyzotero import zotero

from colifer.config import Config
from colifer.namingrules import NamingRules
from colifer.reportextenders.report_extender import ReportExtender

SECTION_SEPARATOR = '/'
DEFAULT_LABEL_RULE = "Default"


class ZoteroParser(ReportExtender):

    def __init__(self, section_entries):
        super().__init__(section_entries)
        if Config.get_section_param(section_entries, "enabled"):
            library_id = Config.get_section_param(section_entries, "library_id")
            api_key = Config.get_section_param(section_entries, "api_key")
            self.read_tag = Config.get_section_param(section_entries, "read_tag")
            library_type = Config.get_section_param(section_entries, "library_type")
            self.zotero_api = zotero.Zotero(library_id, library_type, api_key)
            self.naming_rules = NamingRules()
            naming_rules_filename = Config.get_section_param(section_entries, "naming_rules_file")
            self.naming_rules.read_naming_rules(naming_rules_filename)
        else:
            self.zotero_api = None

    def extend_report(self, report, report_parameters):
        if self.zotero_api:
            path = self.naming_rules.get_path(DEFAULT_LABEL_RULE)
            if path is None:
                print("You must put Default path to Zotero naming rules file")
                exit(1)

            init_section_path_elements = path.split(SECTION_SEPARATOR)
            report.find_or_create_section(report.root_section, init_section_path_elements, False)

            items = self.zotero_api.items(tag=self.read_tag, sort="dateModified")
            if items is not None and len(items) > 0:
                for item in items:
                    item_date = datetime.strptime(item['data']['dateModified'], '%Y-%m-%dT%H:%M:%SZ')
                    item_title = item['data']['title']
                    item_url = item['data']['url']
                    section_path_elements = init_section_path_elements.copy()
                    if report_parameters.period_start <= item_date <= report_parameters.period_end:
                        init_section_path_elements = section_path_elements.copy()
                        print("Processing Zotero article: " + item_title)
                        # TODO: Find a way to make links agnostic to generated format (atm it's md)
                        section_path_elements.append("[{}]({})".format(item_title, item_url))
                        report.find_or_create_section(report.root_section, section_path_elements, False)
