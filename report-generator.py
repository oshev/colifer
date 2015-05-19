import configparser
import csv

if __name__ == '__main__':
    config = configparser.RawConfigParser()
    config.read('report-generator.ini')
    jiffyReport = config['Main' ]['jiffy_report']
    print(jiffyReport)
    with open(jiffyReport, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)

