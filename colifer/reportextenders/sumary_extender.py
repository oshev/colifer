from colifer.config import Config
from report_extender import ReportExtender
SPECIAL_PREV = "PREV"
SECTION_SEPARATOR = '/'


class SummaryExtender(ReportExtender):

    def __init__(self, section_entries):
        super().__init__(section_entries)
        self.summary_path = Config.get_section_param(section_entries, "summary_path")

    def extend_report(self, report, report_parameters):
        section_path_elements = self.summary_path.split(SECTION_SEPARATOR)

        if report.root_section.stats and report.root_section.stats.unit_stats:
            focused_time = int(round((report.root_section.stats.unit_stats.done_pomodoros * 25 * 60) /
                                     report.root_section.stats.seconds * 100))
            focused_info = "{}% of highly focused time (ratio allTime/pomodoroTime).".\
                format(focused_time)
            report.find_or_create_leaf(section_path_elements, focused_info)

            if report.root_section.stats.unit_stats.planned:
                units_from_planned = int(round(report.root_section.stats.unit_stats.done_units_plan /
                                               report.root_section.stats.unit_stats.planned * 100))
                accomplished_info = "{}% units accomplished (ratio done from planned / planned.)". \
                    format(units_from_planned)
                report.find_or_create_leaf(section_path_elements, accomplished_info)



