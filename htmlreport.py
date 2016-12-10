class HtmlReport:

    def traverse_and_save(self, html_file, section, level):
        nice_stats = str(section.stats) if section.stats else ''
        if section.stats and len(section.stats.all_tags) != len(section.stats.common_tags) \
                and len(section.children) == 0:
            all_tags = section.stats.all_tags
        else:
            all_tags = None
        if section.name != 'Dummy':
            html_file.write("{}<li{}>{}{}{}</li>\n".
                            format(self.num_spaces(level),
                                   " class='level{}'".format(level) if section.holds_level_tag else "",
                                   section.name,
                                   "<br><span class='stats'>({})</span>".
                                   format(", ".join(sorted(list(all_tags)))) if all_tags else '',
                                   "<br><span class='stats'>{}</span>".
                                   format(nice_stats) if nice_stats != '' else ''))

            if section.children is not None and len(section.children) > 0:
                html_file.write(self.num_spaces(level) + '<ul>\n')
                for child in section.children:
                    self.traverse_and_save(html_file, child, level + 1)

                if section.stats is not None and section.stats.comments_list is not None:
                    for comment in section.stats.comments_list:

                        html_file.write('{}<li>{}</li>\n'.format(self.num_spaces(level), comment))

                html_file.write(self.num_spaces(level) + '</ul>\n')

    def generate(self, report, filename, before_report, after_report):
        html_file = open(filename, "w")
        html_file.write(before_report + '\n')
        html_file.write('<center><h1>{}</h1></center>'.format(report.title))
        html_file.write('<ul>\n')
        self.traverse_and_save(html_file, report.root_section, 1)
        html_file.write('</ul>\n')
        html_file.write('<br>' + '\n')
        html_file.write(after_report + '\n')
        html_file.close()

    @staticmethod
    def num_spaces(num):
        spaces = ''
        for counter in range(1, num):
            spaces += '\t'
        return spaces
