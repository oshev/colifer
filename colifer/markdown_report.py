from reporting import Section, Report

MAX_HEADER_LEVEL = 4


class MarkdownReport:

    def traverse_and_save(self, md_file, section, level):
        if section.name == 'Dummy':
            return
        stats_line = days_line = ''
        is_header_level_section = section.holds_level_tag and level + 1 <= MAX_HEADER_LEVEL
        # add statistics line (e.g. "(00:32, 2 times, 1 days) <!--11/05 Thu-->" only if useful
        # skip stats for header sections with only 1 child (one child in header sections is always
        # a Dummy section to make sure these sections are not deleted as empty)
        if section.stats and (not is_header_level_section or len(section.children) > 2):
            stats_line = f"*{str(section.stats)}*"
            days_line = f"<!--{section.stats.get_sorted_and_formatted_days()}-->"
        if is_header_level_section:
            prefix_spaces = self.fill(level + 1)
            section_name = f"\n{prefix_spaces} {section.name}\n"
        else:
            prefix_spaces = self.fill(level + 1 - MAX_HEADER_LEVEL, '  ')
            section_name = f"{prefix_spaces}- **{section.name}**"
        all_tags = None
        # print tags only for section where several items with the same name have different tag set
        if (section.stats and len(section.stats.all_tags) != len(section.stats.common_tags)
                and len(section.children) == 0):
            all_tags = section.stats.all_tags
        tags_line = f" *{', '.join(sorted(list(all_tags)))}*" if all_tags else ''
        md_file.write(f"{section_name} {tags_line} {stats_line} {days_line}\n")
        if section.children is not None and len(section.children) > 0:
            for child in section.children:
                self.traverse_and_save(md_file, child, level + 1)

            if section.stats is not None and section.stats.comments_list is not None:
                for comment in section.stats.comments_list:
                    md_file.write(f'{self.fill(level)}-{comment}\n')

    @staticmethod
    def prune_report(report: Report) -> None:
        """
        Remove higher levels up to the header sections for levels containing only 1 child.

        E.g. "header1 -> section1 -> section2 -> section3" will become just "header1 -> section3",
        and
        "header2 -> section4 -> section5 -> section7
                             -> section6"
        will become  "header2 -> section4 -> section7
                                          -> section6"

        :param report: Report to prune.
        :return: None, the action is done in-place (the original object is modified).
        """
        current_section = report.root_section
        for child in current_section.children:
            pass  # TODO

    def generate(self, report, filename, before_report, after_report):
        md_file = open(filename, "w")
        if before_report:
            md_file.write(before_report + '\n')
        md_file.write(f'# {report.title}\n')
        self.traverse_and_save(md_file, report.root_section, 1)
        md_file.write('\n')
        if after_report:
            md_file.write(after_report + '\n')
        md_file.close()

    @staticmethod
    def fill(num, filler='#'):
        spaces = ''
        for _ in range(0, num - 1):
            spaces += filler
        return spaces
