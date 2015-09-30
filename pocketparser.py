import pocket

class PocketParser:

    api = None

    def __init__(self, pocket_consumer_key, pocket_access_token):
        self.api = pocket.Pocket.Api(consumer_key=pocket_consumer_key, access_token=pocket_access_token)

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

            items_list = self.api.get(state = 'archive', sort = 'newest', detailType = 'simple')
            for item in items_list:
                print("%s (%s)" % (item.title, item.resolved_url))
