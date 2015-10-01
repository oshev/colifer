import pocket
import datetime

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

    def load_data(self, naming_rules_filename, report):
        if self.api != '':
            naming_rules = self.read_naming_rules(naming_rules_filename)

            result = self.api.get(state = 'archive', sort = 'newest', detailType = 'simple')
            if result is not None and len(result) > 0 and result[0]['list'] is not None:
                for key in result[0]['list'].keys():
                    print("%s (%s, %s, %s)" % (result[0]['list'][key]['resolved_title'], result[0]['list'][key]['resolved_url'],
                        result[0]['list'][key]['word_count'], datetime.datetime.fromtimestamp(int(result[0]['list'][key]['time_read'])).strftime('%Y-%m-%d')))
                    # time_read, excerpt