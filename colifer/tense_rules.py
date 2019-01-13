class TenseRules:

    def __init__(self):
        super().__init__()
        self.tense_rules = None

    def read_tense_rules(self, tense_rules_filename):
        self.tense_rules = {}
        lines = [line.strip() for line in open(tense_rules_filename)]
        for row in lines:
            if row != '' and not row.startswith('#'):
                verb, new_verb = row.split(' ', 2)
                if verb and new_verb:
                    self.tense_rules[verb.lower()] = new_verb.lower()

    def convert_tense(self, text):
        if not text:
            return text
        if " " in text:
            first_word, rest = text.strip().split(" ", 1)
        else:
            first_word, rest = text, ""
        first_word = first_word.lower()
        if first_word in self.tense_rules:
            first_word = self.tense_rules[first_word]
            first_word = first_word[0].upper() + first_word[1:]
            return (first_word + " " + rest).strip()
        return text
