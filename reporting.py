SECTION_SEPARATOR = '/'

class Section:
    name = ''
    children = None
    stats = None
    entries = None  # list of text entries (or simply put 'what have been done')

    def __init__(self, name):
        self.name = name
        self.children = []

    def __repr__(self):
            return "{\"Name\": \"" + str(self.name) + "\"" + \
                   ", \"Stats\": " + ("\"None\"" if self.stats is None else str(self.stats)) + \
                   ", \"Entries\": " + ("\"None\"" if self.entries is None else str(self.entries)) + \
                   ", \"Children\": " + ("\"None\"" if self.children is None else str(self.children)) + "}"

class Report:
    title = ''
    root_section = None

    def __init__(self):
        sections = []

    def __repr__(self):
            return "{\"Title\": \"" + str(self.title) + "\"" + \
                   ", \"Root\": " + ("\"None\"" if self.root_section is None else str(self.root_section)) + "}"

    def find_or_create_section(self, current_section, section_path_elements, element_index):
        next_section_name = section_path_elements[element_index]
        next_section = None
        for section in current_section.children:
            if section.name == next_section_name:
                next_section = section
                break
        if next_section is None:
            next_section = Section(next_section_name)
            current_section.children.append(next_section)
        if len(section_path_elements) == element_index + 1:
            return next_section
        else:
            return self.find_or_create_section(next_section, section_path_elements, element_index + 1)

    def create(self, name, naming_rules_filename, rows_stats_map):
        lines = [line.strip() for line in open(naming_rules_filename)]
        self.title = name
        self.root_section = Section("Total")
        for row in lines:
            if row != '' and not row.startswith('#'):
                elements = row.split('=')
                if len(elements) == 2:
                    jiffy_id = elements[0]
                    section_path_elements = elements[1].split(SECTION_SEPARATOR)
                    if jiffy_id in rows_stats_map.keys():
                        section = self.find_or_create_section(self.root_section, section_path_elements, 0)
                        section.stats = rows_stats_map[jiffy_id]

