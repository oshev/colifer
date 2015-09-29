from reporting import SECTION_SEPARATOR
import sectionstat

class PocketParser:

    api_key = ''
    user_oauth_token = ''

    def __init__(self, api_key, oauth_token):
        self.api_key = api_key
        self.user_oauth_token = oauth_token

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

    def load_data(self, naming_rules_filename, report):
        if self.api_key != '' and self.user_oauth_token != '':

            naming_rules = self.read_naming_rules(naming_rules_filename)

