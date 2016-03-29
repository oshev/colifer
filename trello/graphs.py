from matplotlib import pyplot as plt
import numpy as np


class TrelloGraphs:

    # See: http://matplotlib.org/examples/pylab_examples/barchart_demo.html
    @staticmethod
    def make_lists_stats_graph(filename, list_names, lists_stats):
        units_done = []
        pomodoros_done = []
        units_failed = []

        for list_name in list_names:
            units_done.append(lists_stats[list_name].units_done)
            pomodoros_done.append(lists_stats[list_name].pomodoros_done)
            units_failed.append(lists_stats[list_name].units_failed)
        # TODO: move constant values to constant variables
        opacity = 0.4
        bar_width = 0.27
        index = np.arange(7)
        ax = plt.subplot(111)
        plt.xticks(index + bar_width * 1.5, list_names)
        plt.bar(index, units_done, bar_width, alpha=opacity, color='b', label='Units done')
        plt.bar(index + bar_width, pomodoros_done, bar_width, alpha=opacity, color='g', label='Poms done')
        plt.bar(index + bar_width * 2, units_failed, bar_width, alpha=opacity, color='r', label='Units failed')
        plt.ylabel('Units')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=False, ncol=5)
        plt.title('Units by days')
        plt.savefig(filename)
        plt.close()
