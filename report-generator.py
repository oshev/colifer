import configparser
import csv

class JiffyCSVParser:
    column_name_project = ''
    column_name_task = ''
    column_name_minutes = ''
    column_name_extra = ''
    time_by_row_id = {}
    extra_by_row_id = {}

    def load_column_names(self):
        self.column_name_project = config['Main']['column_name_project']
        self.column_name_task = config['Main']['column_name_task']
        self.column_name_minutes = config['Main']['column_name_minutes']
        self.column_name_extra = config['Main']['column_name_extra']

    def check_titles(self, titles):
        if titles[self.column_name_project] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_project + ' in CSV')
        if titles[self.column_name_task] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_task + ' in CSV')
        if titles[self.column_name_minutes] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_minutes + ' in CSV')
        if titles[self.column_name_extra] is None:
            raise NameError('Can\'t find necessary column ' + self.column_name_extra + ' in CSV')

    def load_file(self, filename):
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            titles = {}
            for row in reader:
                print(row)
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
                        row_id = row[titles[self.column_name_project]] + '/' + row[titles[self.column_name_task]]
                    if row_id in self.time_by_row_id.keys():
                        accumulated_time = self.time_by_row_id[row_id]
                    else:
                        accumulated_time = 0
                    accumulated_time += int(row[titles[self.column_name_minutes]])
                    self.time_by_row_id[row_id] = accumulated_time

                    if row[titles[self.column_name_extra]] != '' and row[titles[self.column_name_extra]].isdigit():
                        if row_id in self.extra_by_row_id.keys():
                            accumulated_extra = self.extra_by_row_id[row_id]
                        else:
                            accumulated_extra = 0
                        accumulated_extra += int(row[titles[self.column_name_extra]])
                        self.extra_by_row_id[row_id] = accumulated_extra

            print(self.time_by_row_id)
            print(self.extra_by_row_id)


if __name__ == '__main__':
    config = configparser.RawConfigParser()
    config.read('report-generator.ini')
    jiffy_report = config['Main']['jiffy_report_file']

    jiffyCsvParser = JiffyCSVParser()
    jiffyCsvParser.load_column_names()
    jiffyCsvParser.load_file(jiffy_report)

