from config import Config
from reportextenders.report_extender import ReportExtender


class JawBoneSleep(ReportExtender):

    def __init__(self, section_entries):
        super().__init__(section_entries)
        if Config.get_section_param(section_entries, "enabled"):
            self.api = True
        else:
            self.api = None

    def extend_report(self, report, report_parameters):
        if not self.api:
            pass
        pass


