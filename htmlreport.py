class HtmlReport:

    @staticmethod
    def get_nice_stats(stats):
        text = ''
        if stats is not None:
            text = '('
            if stats.time > 0:
                text += "{:02d}:{:02d}, ".format(stats.time // 60, stats.time % 60)
            if stats.extra > 0:
                text += "{:d} words, ".format(stats.extra)
            if stats.events_num > 0:
                text += "{:d} times, ".format(stats.events_num)
            if stats.days_num > 0:
                text += "{:d} days, ".format(stats.days_num)
            if stats.days_list is not None and len(stats.days_list) > 0:
                for day in stats.days_list:
                    text += day + ", "
            if stats.pomodoros_stat is not None and stats.pomodoros_stat.is_not_zero():
                text += stats.pomodoros_stat.__str__()
            text = text.strip(', ')
            text += ')'
        return text

    def traverse_and_save(self, html_file, section, level):
        html_file.write("{}<li{}>{} <span class='stats'>{}</span></li>\n".
                        format(self.num_spaces(level),
                               " class='level{}'".format(level) if section.holds_level_tag else "",
                               section.name,
                               self.get_nice_stats(section.stats)))

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
