class NamingRules:

    def __init__(self):
        super().__init__()
        self.naming_rules = None

    def read_naming_rules(self, naming_rules_filename):
        self.naming_rules = {}
        lines = [line.strip() for line in open(naming_rules_filename)]
        for row in lines:
            if row != '' and not row.startswith('#'):
                tags, path = row.split('=', 2)
                if tags and path:
                    tags_list = tags.split(',')
                    tags = ','.join(sorted(tags_list))
                    self.naming_rules[tags] = path

    def read_naming_rules_old(self, naming_rules_filename):
        self.naming_rules = {}
        lines = [line.strip() for line in open(naming_rules_filename)]
        for row in lines:
            if row != '' and not row.startswith('#'):
                elements = row.split('=')
                if len(elements) == 2:
                    self.naming_rules[elements[0]] = elements[1]