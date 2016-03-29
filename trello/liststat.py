class TrelloListStat:
    def __init__(self):
        super().__init__()
        self.units_done = 0
        self.pomodoros_done = 0
        self.units_failed = 0

    def add_card_stats(self, extended_card):
        self.units_done += extended_card.stats.pomodoros_stat.units
        self.units_failed += extended_card.stats.pomodoros_stat.not_done
        self.pomodoros_done += extended_card.stats.pomodoros_stat.done
