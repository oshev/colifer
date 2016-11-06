from collections import OrderedDict

import numpy as np
from matplotlib import pyplot as plt


class MeasureBar:
    def __init__(self, color):
        self.color = color
        self.values = []

PLANNED_BAR_NAME = "Plan"
UNITS_DONE_BAR_NAME = 'Done'
PLAN_UNITS_DONE_BAR_NAME = 'PlanDone'
POMS_DONE_BAR_NAME = 'PomDone'
UNITS_FAILED_BAR_NAME = "Fail"
BAR_OPACITY = 0.4


class TrelloGraphs:

    # See: http://matplotlib.org/examples/pylab_examples/barchart_demo.html

    @staticmethod
    def make_lists_stats_graph(filename, list_names, lists_stats):
        measure_bars = OrderedDict()
        measure_bars[PLANNED_BAR_NAME] = MeasureBar('y')
        measure_bars[UNITS_DONE_BAR_NAME] = MeasureBar('b')
        measure_bars[PLAN_UNITS_DONE_BAR_NAME] = MeasureBar('c')
        measure_bars[POMS_DONE_BAR_NAME] = MeasureBar('g')
        measure_bars[UNITS_FAILED_BAR_NAME] = MeasureBar('r')

        for list_name in list_names:
            measure_bars[PLANNED_BAR_NAME].values.append(lists_stats[list_name].planned)
            measure_bars[UNITS_DONE_BAR_NAME].values.append(lists_stats[list_name].done_units())
            measure_bars[PLAN_UNITS_DONE_BAR_NAME].values.append(lists_stats[list_name].done_units_plan)
            measure_bars[POMS_DONE_BAR_NAME].values.append(lists_stats[list_name].done_pomodoros)
            measure_bars[UNITS_FAILED_BAR_NAME].values.append(lists_stats[list_name].not_done)

        # TODO: move all constant values to constant variables
        index = np.arange(len(list_names))
        bar_width = 1 / len(measure_bars) * 0.8
        ax = plt.subplot(111)
        plt.xticks(index + bar_width * len(measure_bars) / 2, list_names)
        for pos, measure_bar_item in enumerate(measure_bars.items()):
            plt.bar(index + bar_width * pos, measure_bar_item[1].values, bar_width, alpha=BAR_OPACITY,
                    color=measure_bar_item[1].color, label=measure_bar_item[0])
        plt.ylabel('Units')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=False, ncol=5)
        plt.title('Unit stats by days')
        plt.savefig(filename)
        plt.close()
