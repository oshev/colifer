from colifer.config import Config
from colifer.reportextenders.report_extender import ReportExtender

SPECIAL_PREV = "PREV"
SECTION_SEPARATOR = '/'


class Couple:
    a = ""
    b = ""

    def __init__(self, a, b):
        self.a = a
        self.b = b


class ConstantParser(ReportExtender):

    def __init__(self, section_entries):
        super().__init__(section_entries)
        self.constant_sections_filename = Config.get_section_param(section_entries, "filename")

    @staticmethod
    def read_naming_rules(constant_sections_filename):
        constant_sections = []
        lines = [line.strip() for line in open(constant_sections_filename)]
        for row in lines:
            if row != '' and not row.startswith('#'):
                elements = row.split('=', 1)
                if len(elements) == 2:
                    constant_sections.append(Couple(elements[0], elements[1]))
        return constant_sections

    def extend_report(self, report, report_parameters):
        constant_sections = ConstantParser.read_naming_rules(self.constant_sections_filename)
        prev_section_path_elements = None
        for constant_section in constant_sections:
            if constant_section.a == SPECIAL_PREV and prev_section_path_elements is not None:
                section_path_elements = prev_section_path_elements
            else:
                section_path_elements = constant_section.a.split(SECTION_SEPARATOR)

            section_path_elements.append(constant_section.b)

            report.find_or_create_section(report.root_section, section_path_elements, True)
            prev_section_path_elements = section_path_elements



