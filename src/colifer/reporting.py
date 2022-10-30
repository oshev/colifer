import sectionstats


class Section:
    parent = None
    name = ''
    children = None
    stats = None
    holds_level_tag = False

    def __init__(self, name):
        self.name = name
        self.children = []

    def __repr__(self):
        return "{\"Name\": \"" + str(self.name) + "\"" + \
               ", \"Stats\": " + ("\"None\"" if self.stats is None else str(self.stats)) + \
               ", \"Children\": " + (
                   "\"None\"" if self.children is None else str(self.children)) + "}"


class Report:
    title = ''
    root_section = None

    def __repr__(self):
        return "{\"Title\": \"" + str(self.title) + "\"" + \
               ", \"Root\": " + (
                   "\"None\"" if self.root_section is None else str(self.root_section)) + "}"

    def find_or_create_section(self, current_section, section_path_elements, holds_level_tag):
        next_section_name = section_path_elements[0]
        next_section = None
        for section in current_section.children:
            if section.name == next_section_name:
                next_section = section
                break
        if next_section is None:
            next_section = Section(next_section_name)
            next_section.parent = current_section
            next_section.holds_level_tag = holds_level_tag
            current_section.children.append(next_section)
        if len(section_path_elements) == 1:
            return next_section
        else:
            return self.find_or_create_section(next_section, section_path_elements[1:],
                                               holds_level_tag)

    def find_or_create_leaf(self, init_section_path_elements, leaf_element, holds_level_tag=False):
        section_path_elements = init_section_path_elements.copy()
        section_path_elements.append(leaf_element)
        return self.find_or_create_section(self.root_section, section_path_elements,
                                           holds_level_tag)

    @staticmethod
    def propagate_stats_to_parent(section, stats):
        if section.parent is not None:
            if section.parent.stats is None:
                section.parent.stats = sectionstats.SectionStats()
            section.parent.stats.add_stats(stats)

            Report.propagate_stats_to_parent(section.parent, stats)

    def create(self, name):
        self.title = name
        self.root_section = Section("Total")
        self.root_section.holds_level_tag = True
