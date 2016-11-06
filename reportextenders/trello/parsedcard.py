from sectionstats import UnitStats


class TrelloParsedCard:
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.title = "Error"
        self.title_past = "Error"
        self.children = []
        self.unit_stats = UnitStats()

    def add_child(self, value):
        self.children.append(value)
