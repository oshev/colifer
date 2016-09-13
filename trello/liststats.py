class TrelloListStats:
    def __init__(self):
        self.planned = 0
        self.done_units = 0
        self.done_pomodoros = 0
        self.not_done = 0

    def add_card_stats(self, extended_card):
        unit_stats = extended_card.stats.unit_stats
        self.planned += unit_stats.planned
        self.done_units += unit_stats.done_units()
        self.done_pomodoros += unit_stats.done_pomodoros
        self.not_done += unit_stats.not_done()
