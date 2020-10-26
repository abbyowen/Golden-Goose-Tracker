#Author: Abby Owen
#Purpose: Hold shoe objects

class Shoe:

    # Instance variables that will hold various features of the shoe
    def __init__(self, description, size, price, href, pID):
        self.description = description
        self.size = size
        self.price = price
        self.href = href
        self.pID = pID

    # Function for comparing two objects by their shoe IDs
    def __eq__(self, obj):
        if self.pID == obj.pID:
            return True
        else:
            return False

    # String representation of the shoe
    def __str__(self):
        return self.description + "," + self.size + "," + self.price + "," + self.href + "," + self.pID
