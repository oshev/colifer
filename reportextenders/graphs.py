import numpy as np
from matplotlib import pyplot as plt


class Graphs:

    def __init__(self):
        super().__init__()

    @staticmethod
    def save_line_graph(filename, title, measures_ordered_dict,
                        x_tics, y_label, y_min, y_max, legend_y=-0.23, legend_columns=3, y_tick_step=1):

        index = np.arange(len(x_tics))
        fig, ax = plt.subplots()
        ax.yaxis.set_ticks([t for t in range(y_min, y_max, y_tick_step)])
        ax.grid(True, which='both')
        fig.autofmt_xdate()
        ax.set_ylim((y_min, y_max))
        plt.xticks(index, x_tics)
        for pos, measures_item in enumerate(measures_ordered_dict.items()):
            ax.plot(index, measures_item[1].values,
                    color=measures_item[1].color, label=measures_item[0], linewidth=1)
        plt.ylabel(y_label)
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, legend_y), fancybox=True, shadow=False, ncol=legend_columns)
        plt.title(title)
        plt.savefig(filename)
        plt.close()
