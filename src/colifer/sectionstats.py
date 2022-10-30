class SectionStats:

    def add_stats(self, stats):
        self.seconds += stats.seconds
        self.words_num += stats.words_num
        self.events_num += stats.events_num
        self.days = self.days.union(stats.days)
        self.all_tags = self.all_tags.union(stats.all_tags)
        self.common_tags = self.common_tags.intersection(stats.common_tags)

    def __init__(self, path='', seconds=0, words_num=0, tags=set(),
                 events_num=1, days=set(), comments_list=None):
        self.path = path
        self.seconds = seconds
        self.words_num = words_num
        self.all_tags = tags
        self.common_tags = tags
        self.events_num = events_num
        self.days = days
        self.comments_list = comments_list if comments_list else []

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
            text += "{:d} days; ".format(len(self.days))
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
               ", \"Comments list\": " + ("\"None\"" if self.comments_list is None else str(self.comments_list)) + "}"
