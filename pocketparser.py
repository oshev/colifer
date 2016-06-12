import datetime

import pocket

from namingrules import NamingRules
from reporting import SECTION_SEPARATOR

DEFAULT_LABEL_RULE = "Default"


class PocketParser:
    api = None

    def __init__(self, pocket_consumer_key, pocket_access_token):
        self.api = pocket.Pocket(pocket_consumer_key, pocket_access_token)
        self.naming_rules = NamingRules()

    @staticmethod
    def safe_get(article, field, alternative):
        if field in article:
            return article[field]
        elif alternative:
            return article[alternative]
        else:
            return ''

    def load_data(self, report, week_start, week_end, naming_rules_filename):
        if self.api != '':
            self.naming_rules.read_naming_rules_old(naming_rules_filename)

            path = self.naming_rules.get_path(DEFAULT_LABEL_RULE)
            if path is None:
                print("You must put Default path to Pocket naming rules file")
                exit(1)

            init_section_path_elements = path.split(SECTION_SEPARATOR)
            init_section_path_elements.append("Read articles")
            report.find_or_create_section(report.root_section, init_section_path_elements, 0, False)
            init_section_path_elements.append("Quora")
            report.find_or_create_section(report.root_section, init_section_path_elements, 0, False)
            init_section_path_elements.pop()

            result = self.api.get(state='archive', detailType='simple')
            if result is not None and len(result) > 0 and result[0]['list'] is not None:
                for key in result[0]['list'].keys():
                    section_path_elements = init_section_path_elements.copy()
                    time_read = datetime.datetime.fromtimestamp(int(result[0]['list'][key]['time_read']))
                    if week_start <= time_read <= week_end:
                        init_section_path_elements = section_path_elements.copy()
                        if "quora.com" in self.safe_get(result[0]['list'][key], 'resolved_url', 'given_url'):
                            section_path_elements.append("Quora")
                        print("Processing Pocket article: " + self.safe_get(result[0]['list'][key],
                                                                            'resolved_title', 'given_title'))
                        section_path_elements.append("<a href='" +
                                                     self.safe_get(result[0]['list'][key],
                                                                   'resolved_url', 'given_url') +
                                                     "'>" +
                                                     self.safe_get(result[0]['list'][key],
                                                                   'resolved_title', 'given_title') +
                                                     "</a>" +
                                                     " (" + self.safe_get(result[0]['list'][key], 'word_count', None) +
                                                     "&nbsp;words)")
                        report.find_or_create_section(report.root_section, section_path_elements, 0, False)
