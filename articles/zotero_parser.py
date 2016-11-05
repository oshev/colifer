from datetime import datetime
from pyzotero import zotero
from namingrules import NamingRules
from reporting import SECTION_SEPARATOR

DEFAULT_LABEL_RULE = "Default"


class ZoteroParser:
    api = None

    def __init__(self, library_id, library_type, api_key, read_tag):
        library_id = library_id
        api_key = api_key
        self.read_tag = read_tag
        self.naming_rules = NamingRules()
        self.zotero_api = zotero.Zotero(library_id, library_type, api_key)

    def load_data(self, report, week_start, week_end, naming_rules_filename):
        if self.api != '':
            self.naming_rules.read_naming_rules_old(naming_rules_filename)

            path = self.naming_rules.get_path(DEFAULT_LABEL_RULE)
            if path is None:
                print("You must put Default path to Zotero naming rules file")
                exit(1)

            init_section_path_elements = path.split(SECTION_SEPARATOR)
            init_section_path_elements.append("Read articles")
            report.find_or_create_section(report.root_section, init_section_path_elements, 0, False)
            init_section_path_elements.pop()

            items = self.zotero_api.items(tag=self.read_tag, sort="dateModified")
            if items is not None and len(items) > 0:
                for item in items:
                    item_date = datetime.strptime(item['data']['dateModified'], '%Y-%m-%dT%H:%M:%SZ')
                    item_title = item['data']['title']
                    item_url = item['data']['url']
                    section_path_elements = init_section_path_elements.copy()
                    if week_start <= item_date <= week_end:
                        init_section_path_elements = section_path_elements.copy()
                        print("Processing Zotero article: " + item_title)
                        section_path_elements.append("<a href='{}'>{}</a>".format(item_url, item_title))
                        report.find_or_create_section(report.root_section, section_path_elements, 0, False)
