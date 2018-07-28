MAX_HEADER_LEVEL = 3


class MarkdownReport:

    def traverse_and_save(self, md_file, section, level):
        nice_stats = str(section.stats) if section.stats else ''
        if section.stats and len(section.stats.all_tags) != len(section.stats.common_tags) \
                and len(section.children) == 0:
            all_tags = section.stats.all_tags
        else:
            all_tags = None
        if section.name != 'Dummy':
            if all_tags:
                tags_line = "\n{}{}".format(self.fill(level + 1), "*{}*".format(", ".join(sorted(list(all_tags)))))
            else:
                tags_line = ''
            if nice_stats:
                stats_line = "\n{}{}".format(self.fill(level + 1), "*{}*".format(nice_stats))
            else:
                stats_line = ''
            if section.holds_level_tag and level + 1 <= MAX_HEADER_LEVEL:
                section_name = "{} {}".format(self.fill(level + 1, '#'), section.name)
            else:
                section_name = "**{}**".format(section.name)

            md_file.write("{}- {}{}{}\n".format(self.fill(level), section_name,
                                                tags_line, stats_line))

            if section.children is not None and len(section.children) > 0:
                for child in section.children:
                    self.traverse_and_save(md_file, child, level + 1)

                if section.stats is not None and section.stats.comments_list is not None:
                    for comment in section.stats.comments_list:

                        md_file.write('{}- {}\n'.format(self.fill(level), comment))

    def generate(self, report, filename, before_report, after_report):
        md_file = open(filename, "w")
        if before_report:
            md_file.write(before_report + '\n')
        md_file.write('# {}\n'.format(report.title))
        self.traverse_and_save(md_file, report.root_section, 1)
        md_file.write('\n')
        if after_report:
            md_file.write(after_report + '\n')
        md_file.close()

    @staticmethod
    def fill(num, filler='  '):
        spaces = ''
        for counter in range(0, num - 1):
            spaces += filler
        return spaces
