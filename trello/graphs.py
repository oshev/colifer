import numpy as np
from matplotlib import pyplot as plt


class TrelloGraphs:

    # See: http://matplotlib.org/examples/pylab_examples/barchart_demo.html
    @staticmethod
    def make_lists_stats_graph(filename, list_names, lists_stats):
        planned = []
        done_units = []
        done_pomodoros = []
        not_done = []

        for list_name in list_names:
            planned.append(lists_stats[list_name].planned)
            done_units.append(lists_stats[list_name].done_units)
            done_pomodoros.append(lists_stats[list_name].done_pomodoros)
            not_done.append(lists_stats[list_name].not_done)
        # TODO: move constant values to constant variables
        opacity = 0.4
        bar_width = 0.27
        index = np.arange(7)
        ax = plt.subplot(111)
        plt.xticks(index + bar_width * 1.5, list_names)
        plt.bar(index, planned, bar_width, alpha=opacity, color='b', label='Planned')
        plt.bar(index + bar_width * 1, done_units, bar_width, alpha=opacity, color='b', label='Units done')
        plt.bar(index + bar_width * 2, done_pomodoros, bar_width, alpha=opacity, color='g', label='Poms done')
        plt.bar(index + bar_width * 3, not_done, bar_width, alpha=opacity, color='r', label='Units failed')
        plt.ylabel('Units')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=False, ncol=5)
        plt.title('Units by days')
        plt.savefig(filename)
        plt.close()
