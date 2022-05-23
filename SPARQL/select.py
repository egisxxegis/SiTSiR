class Select:
    def __init__(self):
        self.variables_arr = []
        self.isDistinct = False

    def variable_add(self, variable: str):
        self.variables_arr.append(variable)
