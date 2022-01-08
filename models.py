class Item:
    def __init__(self):
        self.id = -1
        self.message = ""
    def __init__(self, id, message):
        self.id = id
        self.message = message

class MultiItems:
    def __init__(self):
        self.message = ""
        self.items = []

    def __init__(self, message, items):
        self.message = message
        self.items = items

    def __str__(self):
        return f"message:{self.message} items:{self.items}"