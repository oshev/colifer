class PastTenseRules:

    def __init__(self):
        super().__init__()
        self.past_tense_rules = None

    def read_past_tense_rules(self, past_tense_rules_filename):
        self.past_tense_rules = {}
        lines = [line.strip() for line in open(past_tense_rules_filename)]
        for row in lines:
            if row != '' and not row.startswith('#'):
                present, past = row.split(' ', 2)
                if present and past:
                    self.past_tense_rules[present.lower()] = past.lower()

    def convert_to_past(self, text):
        if not text:
            return text
        if " " in text:
            first_word, rest = text.split(" ", 1)
        else:
            first_word, rest = text, ""
        first_word = first_word.lower()
        if first_word in self.past_tense_rules:
            first_word = self.past_tense_rules[first_word]
            first_word = first_word[0].upper() + first_word[1:]
            return (first_word + " " + rest).strip()
        return text
