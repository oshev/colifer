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

    done_single = 0
    done_double = 0

    def is_not_zero(self):
        return self.planned > 0 or self.done > 0 or self.broken > 0 or self.not_done > 0

    def add_pomodoros(self, pomodoros_stat):
        self.planned += pomodoros_stat.planned
        self.done += pomodoros_stat.done
        self.broken += pomodoros_stat.broken
        self.not_done += pomodoros_stat.not_done
        self.done_single += pomodoros_stat.done_single
        self.done_double += pomodoros_stat.done_double

    def __repr__(self):
        return "{\"Planned\": " + str(self.planned) + \
               ", \"Done Total\": " + str(self.done) + \
               ", \"Broken\": " + str(self.broken) + \
               ", \"Not done\": " + str(self.not_done) + \
               ", \"Done single\": " + str(self.done_single) + \
               ", \"Done double\": " + str(self.done_double) + "}"

    def __str__(self):
        return "Pomodoros [" + \
            "{}".format("Planned: " + str(self.planned) + ", " if self.planned > 0 else "") + \
            "{}".format("Broken: " + str(self.broken) + ", " if self.broken > 0 else "") + \
            "{}".format("Not done: " + str(self.not_done) + ", " if self.not_done > 0 else "") + \
            "{}".format("Done: " + str(self.done) +
                        (" (single " + str(self.done_single) + ", "
                            if self.done_single > 0 and self.done_double > 0 else "") +
                        (" (" if self.done_single == 0 else "") +
                        ("double " + str(self.done_double) + ")" if self.done_double > 0 else "")
                        if self.done > 0 else "") + \
            "]".strip(', ') if self.is_not_zero() else ""
