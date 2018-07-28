class SectionStats:

    def add_stats(self, stats):
        self.seconds += stats.seconds
        self.words_num += stats.words_num
        self.events_num += stats.events_num
        self.days = self.days.union(stats.days)
        self.all_tags = self.all_tags.union(stats.all_tags)
        self.common_tags = self.common_tags.intersection(stats.common_tags)
        self.unit_stats.add(stats.unit_stats)

    def __init__(self, path='', seconds=0, words_num=0, tags=set(),
                 events_num=1, days=set(), comments_list=None, unit_stats=None):
        self.path = path
        self.seconds = seconds
        self.words_num = words_num
        self.all_tags = tags
        self.common_tags = tags
        self.events_num = events_num
        self.days = days
        self.comments_list = comments_list if comments_list else []
        self.unit_stats = unit_stats if unit_stats else UnitStats()

    def get_sorted_and_formatted_days(self):
        return ", ".join([day.strftime("%m/%d %a") for day in sorted(list(self.days))])

    def __str__(self):
        text = '('
        if self.seconds > 0:
            text += "{:02d}:{:02d}, ".format((self.seconds // 60) // 60, (self.seconds // 60) % 60)
        if self.words_num > 0:
            text += "{:d} words, ".format(self.words_num)
        if self.events_num > 0:
            text += "{:d} times, ".format(self.events_num)
        if len(self.days) > 0:
            text += "{:d} days: {}; ".format(len(self.days), self.get_sorted_and_formatted_days())
        if self.unit_stats is not None and not self.unit_stats.is_zero():
            text += self.unit_stats.__str__()
        text = text.strip(', ').strip('; ')
        text += ')'
        return text

    def __repr__(self):
        return "{\"Seconds\": " + str(self.seconds) + \
               ", \"Extra\": " + str(self.words_num) + \
               ", \"Events num\": " + str(self.events_num) + \
               ", \"Days num\": " + str(len(self.days)) + \
               ", \"Days\": " + ("\"None\"" if self.days is None
                                                else ", ".join(self.get_sorted_and_formatted_days())) + \
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
                self.fmt_field("unt", self.done_units()) if self.done_units() != self.done_pomodoros else '' +
                self.fmt_field("untPln", self.done_units_plan) +
                self.fmt_field("pom", self.done_pomodoros) +
                self.fmt_field("brk", self.broken_pomodoros) +
                self.fmt_field("fail", self.not_done)).\
                strip(', ') + "]" if not self.is_zero() else ""
