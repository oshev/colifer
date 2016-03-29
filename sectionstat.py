class SectionStat:

    def add_stats(self, stats):
        self.seconds += stats.seconds
        self.extra += stats.extra
        self.events_num += stats.events_num
        self.days_num += stats.days_num

    def __init__(self):
        super().__init__()
        self.jiffy_name = ''
        self.seconds = 0
        self.extra = 0
        self.events_num = 0
        self.days_num = 0
        self.days_list = []
        self.comments_list = []
        self.pomodoros_stat = PomodorosStat()

    def __repr__(self):
        return "{\"Seconds\": " + str(self.seconds) + \
               ", \"Extra\": " + str(self.extra) + \
               ", \"Events num\": " + str(self.events_num) + \
               ", \"Days num\": " + str(self.days_num) + \
               ", \"Days list\": " + ("\"None\"" if self.days_list is None else str(self.days_list)) + \
               ", \"Comments list\": " + ("\"None\"" if self.comments_list is None else str(self.comments_list)) + \
               ", \"Pomodoros stat\": " + ("\"None\"" if self.pomodoros_stat is None else str(self.pomodoros_stat)) + "}"


class PomodorosStat:

    def __init__(self):
        super().__init__()
        self.planned = 0
        self.units = 0
        self.done = 0
        self.broken = 0
        self.not_done = 0

    def is_not_zero(self):
        return self.planned > 0 or self.done > 0 or self.broken > 0 or self.not_done > 0 or self.units > 0

    def add_pomodoros(self, pomodoros_stat):
        self.planned += pomodoros_stat.planned
        self.done += pomodoros_stat.done
        self.broken += pomodoros_stat.broken
        self.not_done += pomodoros_stat.not_done
        self.units += pomodoros_stat.units

    def __repr__(self):
        return "{\"Planned\": " + str(self.planned) + \
               ", \"Units\": " + str(self.units) + \
               ", \"Done Total\": " + str(self.done) + \
               ", \"Broken\": " + str(self.broken) + \
               ", \"Not done\": " + str(self.not_done) + "}"

    @staticmethod
    def fmt_field(name, value):
        return "{}".format(name + ": " + str(int(value) if value - int(value) < 0.0001 else "{:.1f}".format(value)) +
                           ", " if value > 0 else "")

    def __str__(self):
        return ("P[" + self.fmt_field("pln", self.planned) +
                self.fmt_field("unt", self.units) +
                self.fmt_field("pom", self.done) +
                self.fmt_field("brk", self.broken) +
                self.fmt_field("fail", self.not_done)).\
                strip(', ') + "]" if self.is_not_zero() else ""
