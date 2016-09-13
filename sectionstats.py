class SectionStats:

    def add_stats(self, stats):
        self.seconds += stats.seconds
        self.extra += stats.extra
        self.events_num += stats.events_num
        self.days_num += stats.days_num

    def __init__(self):
        self.jiffy_name = ''
        self.seconds = 0
        self.extra = 0
        self.events_num = 0
        self.days_num = 0
        self.days_list = []
        self.comments_list = []
        self.unit_stats = UnitStats()

    def __repr__(self):
        return "{\"Seconds\": " + str(self.seconds) + \
               ", \"Extra\": " + str(self.extra) + \
               ", \"Events num\": " + str(self.events_num) + \
               ", \"Days num\": " + str(self.days_num) + \
               ", \"Days list\": " + ("\"None\"" if self.days_list is None else str(self.days_list)) + \
               ", \"Comments list\": " + ("\"None\"" if self.comments_list is None else str(self.comments_list)) + \
               ", \"Unit stats\": " + ("\"None\"" if self.unit_stats is None else str(self.unit_stats)) + "}"


class UnitStats:

    def __init__(self):
        self.planned = 0
        self.done_cucumbers = 0  # cucumber is a non-focused interval (approx. 25 minutes)
        self.done_pomodoros = 0  # pomodoro is a focused and timed interval (usually 25 minutes)
        self.broken_pomodoros = 0

    def is_not_zero(self):
        return self.planned > 0 or self.done_pomodoros > 0 or self.done_cucumbers > 0 or \
               self.broken_pomodoros > 0 or self.not_done() > 0

    def add(self, unit_stats):
        self.planned += unit_stats.planned
        self.done_cucumbers += unit_stats.done_cucumbers
        self.done_pomodoros += unit_stats.done_pomodoros
        self.broken_pomodoros += unit_stats.broken_pomodoros

    def done_units(self):
        return self.done_cucumbers + self.done_pomodoros

    def not_done(self):
        return self.planned - self.done_units()

    def __repr__(self):
        return "{\"Planned\": " + str(self.planned) + \
               ", \"Units\": " + str(self.done_cucumbers) + \
               ", \"Done Total\": " + str(self.done_pomodoros) + \
               ", \"Broken\": " + str(self.broken_pomodoros) + \
               ", \"Not done\": " + str(self.not_done) + "}"

    @staticmethod
    def fmt_field(name, value):
        return "{}".format(name + ": " + str(int(value) if value - int(value) < 0.0001 else "{:.1f}".format(value)) +
                           ", " if value > 0 else "")

    def __str__(self):
        return ("P[" + self.fmt_field("pln", self.planned) +
                self.fmt_field("unt", self.done_units()) +
                self.fmt_field("pom", self.done_pomodoros) +
                self.fmt_field("brk", self.broken_pomodoros) +
                self.fmt_field("fail", self.not_done())).\
                strip(', ') + "]" if self.is_not_zero() else ""
