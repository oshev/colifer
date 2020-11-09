from typing import Optional


class NamingRules:

    def __init__(self):
        super().__init__()
        self.__content = None

    def get_path(self, tags, text="") -> Optional[str]:
        if tags in self.__content:
            rules = self.__content[tags]
            for (matcher, path) in rules:
                if matcher is None or (text is not None and matcher in text.lower()):
                    return path
        return None

    def read_naming_rules_with_tags(self, naming_rules_filename: str) -> None:
        self.__content = {}
        lines = [line.strip() for line in open(naming_rules_filename)]
        for row in lines:
            if row != '' and not row.startswith('#'):
                tags, path = row.split('=', 2)
                if tags and path:
                    matcher = None
                    if "[" in tags:
                        tags, matcher = tags.split('[', 2)
                        matcher = matcher.replace(']', '').lower()
                    tags_list = tags.split(',')
                    tags = ','.join(sorted(tags_list))
                    if tags not in self.__content:
                        self.__content[tags] = []
                    self.__content[tags].append((matcher, path))

    def read_naming_rules(self, naming_rules_filename: str) -> None:
        self.__content = {}
        lines = [line.strip() for line in open(naming_rules_filename)]
        for row in lines:
            if row != '' and not row.startswith('#'):
                elements = row.split('=')
                if len(elements) == 2:
                    if elements[0] not in self.__content:
                        self.__content[elements[0]] = []
                    self.__content[elements[0]].append((None, elements[1]))
