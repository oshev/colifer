# The interface for all report extenders
class ReportExtender:

    def __init__(self, section_entries):
        self.section_entries = section_entries
        pass

    def extend_report(self, report, report_parameters):
        pass
