class TagOrder:

    def __init__(self, tag_order_filename):
        super().__init__()
        self.__tags = {}
        lines = [line.strip() for line in open(tag_order_filename)]
        order_num = 0
        for row in lines:
            if row and not row.startswith('#'):
                for tag in row.split(","):
                    self.__tags[tag.strip()] = order_num
                order_num += 1

    def get_order(self, tag):
        if tag in self.__tags:
            return self.__tags[tag]
        else:
            return None




