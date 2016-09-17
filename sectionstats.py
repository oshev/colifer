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

    def __init__(self, planned=0, done_cucumbers=0, done_pomodoros=0, broken_pomodoros=0, not_done=0):
        self.planned = planned
        self.done_cucumbers = done_cucumbers  # cucumber is a non-focused interval (approx. 25 minutes)
        self.done_pomodoros = done_pomodoros  # pomodoro is a focused and timed interval (usually 25 minutes)
        self.done_units_plan = min(self.done_units(), planned)
        self.broken_pomodoros = broken_pomodoros
        self.not_done = not_done

    def is_zero(self):
        return not self.planned and not self.done_pomodoros and not self.done_cucumbers and \
               not self.broken_pomodoros and not self.not_done

    def add(self, unit_stats):
        self.planned += unit_stats.planned
        self.done_cucumbers += unit_stats.done_cucumbers
        self.done_pomodoros += unit_stats.done_pomodoros
        self.not_done += unit_stats.not_done
        self.done_units_plan += unit_stats.done_units_plan
        self.broken_pomodoros += unit_stats.broken_pomodoros

    def done_units(self):
        return self.done_cucumbers + self.done_pomodoros

    def __repr__(self):
        return "{\"Plan\": " + str(self.planned) + \
               ", \"Units\": " + str(self.done_cucumbers) + \
               ", \"Units Plan\": " + str(self.done_units_plan) + \
               ", \"Poms\": " + str(self.done_pomodoros) + \
               ", \"Broken\": " + str(self.broken_pomodoros) + \
               ", \"Not done\": " + str(self.not_done) + "}"

    @staticmethod
    def fmt_field(name, value):
        return "{}".format(name + ": " + str(int(value) if value - int(value) < 0.0001 else "{:.1f}".format(value)) +
                           ", " if value > 0 else "")

    def __str__(self):
        return ("S[" + self.fmt_field("pln", self.planned) +
                self.fmt_field("unt", self.done_units()) +
                self.fmt_field("untPln", self.done_units_plan) +
                self.fmt_field("pom", self.done_pomodoros) +
                self.fmt_field("brk", self.broken_pomodoros) +
                self.fmt_field("fail", self.not_done)).\
                strip(', ') + "]" if not self.is_zero() else ""
