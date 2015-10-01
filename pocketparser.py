import pocket
import datetime
from reporting import SECTION_SEPARATOR

DEFAULT_LABEL_RULE = "Default"

class PocketParser:

    api = None

    def __init__(self, pocket_consumer_key, pocket_access_token):
        self.api = pocket.Pocket(pocket_consumer_key, pocket_access_token)

    @staticmethod
    def read_naming_rules(naming_rules_filename):
        naming_rules = {}
        lines = [line.strip() for line in open(naming_rules_filename)]
        for row in lines:
            if row != '' and not row.startswith('#'):
                elements = row.split('=')
                if len(elements) == 2:
                    naming_rules[elements[0]] = elements[1]
        return naming_rules

    def load_data(self, report, week_start, week_end, naming_rules_filename):
        if self.api != '':
            naming_rules = self.read_naming_rules(naming_rules_filename)

            rule = None
            if naming_rules[DEFAULT_LABEL_RULE] is not None:
                rule = naming_rules[DEFAULT_LABEL_RULE]
            else:
                print("You must put Default rule to Pocket naming rules file")
                exit(1)

            init_section_path_elements = rule.split(SECTION_SEPARATOR)
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
                        if "quora.com" in result[0]['list'][key]['resolved_url']:
                            section_path_elements.append("Quora")
                        print("Processing Pocket article: " + result[0]['list'][key]['resolved_title'])
                        section_path_elements.append("<a href='" +
                                                     result[0]['list'][key]['resolved_url'] +
                                                     "'>" +
                                                     result[0]['list'][key]['resolved_title'] +
                                                     "</a>" +
                                                     " (" + result[0]['list'][key]['word_count'] +
                                                     "&nbsp;words)")
                        report.find_or_create_section(report.root_section, section_path_elements, 0, False)

