class SectionStat:
    jiffy_name = ''
    time = 0
    extra = 0
    events_num = 0
    days_num = 0
    days_list = None
    comments_list = None
    pomodoros_stat = None

    def __init__(self):
        super().__init__()
        self.days_list = []
        self.comments_list = []
        self.pomodoros_stat = PomodorosStat()

    def __repr__(self):
        return "{\"Time\": " + str(self.time) + \
               ", \"Extra\": " + str(self.extra) + \
               ", \"Events num\": " + str(self.events_num) + \
               ", \"Days num\": " + str(self.days_num) + \
               ", \"Days list\": " + ("\"None\"" if self.days_list is None else str(self.days_list)) + \
               ", \"Comments list\": " + ("\"None\"" if self.comments_list is None else str(self.comments_list)) + \
               ", \"Pomodoros stat\": " + ("\"None\"" if self.pomodoros_stat is None else str(self.pomodoros_stat)) + "}"

class PomodorosStat:
    planned = 0
    done = 0
    broken = 0
    not_done = 0

    def is_not_zero(self):
        return self.planned > 0 or self.done > 0 or self.broken > 0 or self.not_done > 0

    def __repr__(self):
        return "{\"Planned\": " + str(self.planned) + \
               ", \"Done\": " + str(self.done) + \
               ", \"Broken\": " + str(self.broken) + \
               ", \"Not done\": " + str(self.not_done) + "}"

    def __str__(self):
        return "Pomodoros [Planned: " + str(self.planned) + \
               ", Done: " + str(self.done) + \
               ", Broken: " + str(self.broken) + \
               ", Not done: " + str(self.not_done) + "]"
