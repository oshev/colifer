import csv
import sectionstat

ID_DIV = '-'
ID_TOTAL = 'Total'

class JiffyCSVParser:

    column_name_project = ''
    column_name_task = ''
    column_name_minutes = ''
    column_name_extra = ''
    rows_stats_map = {}
    config = None

    def __init__(self, config):
        super().__init__()
        self.config = config

    def load_column_names(self):
        self.column_name_project = self.config['Columns']['column_name_project']
        self.column_name_task = self.config['Columns']['column_name_task']
        self.column_name_minutes = self.config['Columns']['column_name_minutes']
        self.column_name_extra = self.config['Columns']['column_name_extra']

    def check_titles(self, titles):
        if titles[self.column_name_project] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_project + ' in CSV')
        if titles[self.column_name_task] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_task + ' in CSV')
        if titles[self.column_name_minutes] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_minutes + ' in CSV')
        if titles[self.column_name_extra] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_extra + ' in CSV')

    def update_stat_object(self, row_id, row, titles):
        if row_id in self.rows_stats_map.keys():
            stat_object = self.rows_stats_map[row_id]
        else:
            stat_object = sectionstat.SectionStat()
            stat_object.jiffy_name = row_id
            self.rows_stats_map[row_id] = stat_object

        stat_object.time += int(row[titles[self.column_name_minutes]])

        if row[titles[self.column_name_extra]].isdigit():
            stat_object.extra += int(row[titles[self.column_name_extra]])
        elif row[titles[self.column_name_extra]] != '' and ID_DIV + ID_TOTAL not in row_id:
            stat_object.comments_list.append(row[titles[self.column_name_extra]])

    def load_file(self, filename):
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            titles = {}
            for row in reader:
                if len(titles) == 0:
                    index = 0
                    for col in row:
                        titles[col] = index
                        index += 1
                    self.check_titles(titles)
                else:
                    if row[titles[self.column_name_task]] == '':
                        row_id = row[titles[self.column_name_project]]
                    else:
                        row_id = row[titles[self.column_name_project]] + ID_DIV + row[titles[self.column_name_task]]
                    row_up_id = row[titles[self.column_name_project]] + ID_DIV + ID_TOTAL

                    self.update_stat_object(row_id, row, titles)
                    self.update_stat_object(row_up_id, row, titles)

            # print(self.rows_stats_map)
