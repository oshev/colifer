# CoLifer

CoLifer is a Python-based project that generates yearly, quarterly, monthly, and weekly reports in markdown format. The reports are based on personal data from Toggl, Zotero, and Pocket. The project allows you to define various configurations in the `/config` directory, including a main configuration file named `colifer.yaml`.

## Getting Started

To get started with CoLifer, you need to follow these steps:

1. Clone the CoLifer repository.
1. Inside its folder, create a virtual environment, e.g., `python3.8 -m venv venv`.
1. Activate the environment, e.g., `source venv/bin/activate`.
1. Upgrade pip: `python3.8 -m pip install --upgrade pip`
1. Install the required Python packages from `requirements.txt` using `pip install -r requirements.txt`.
1. Create a copy of the `colifer.sample.yaml` file in the /config directory, name it `colifer.yaml`, and fill in the required configurations.
1. Run the command python `src/colifer/generator.py --year <YEAR> --type <REPORT_TYPE> --period-num <PERIOD_NUM>` to generate a report.

The `<YEAR>` parameter is the year for which the report should be generated, `<REPORT_TYPE>` is the report type (yearly, quarterly, monthly, weekly), and `<PERIOD_NUM>` is the number of the period: quarter (1-4), month (1-12), or week (1-53); depending on the report type.

For generating weekly reports, you can use the script `scripts/gen_weekly_report.sh` that requires only one parameter, the week number. You can call it using the command `scripts/gen_weekly_report.sh 13`.

There is also an additional script that you can run using the command `pocket-stats` (if you install the CoLifer package in your virtual environment). This script prints the unread queue size and the number of archived articles.

## Configuration

All the configurations are in the `/config` directory. The main configuration file is `colifer.yaml`, which allows you to define the report title template, Toggl API calls and token, keys, and parameters for Zotero and Pocket. You can also define constant sections, group Toggl tags, and change verb tenses from present tense in Toggl entries to past tense in the report.

## Generating Reports

To generate a report, you need to run the command python `src/colifer/generator.py --year <YEAR> --type <REPORT_TYPE> --period-num <PERIOD_NUM>`. The generated report will be saved in the directory defined in `colifer.yaml`, see `MarkdownGenerator: out_md_report_file`.

For weekly reports, you can use the script `scripts/gen_weekly_report.sh`. You need to pass the week number as a parameter. 

## Pocket Statistics

To get the unread queue size and the number of archived articles in Pocket, you can use the `pocket-stats` script. This script is available only if you install the CoLifer package in your virtual environment. You can run the script using the command `pocket-stats`.

