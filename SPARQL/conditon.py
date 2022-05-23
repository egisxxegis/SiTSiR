class Condition:
    def __init__(self):
        self.operand_left = ""
        self.operand_right = ""
        self.operator = ""
        self.function = ""
        self.is_function_negated = False
        self.arguments_arr: [str] = []
        self.operator_logical_previous = ""

    def is_complete(self) -> bool:
        if self.is_function():
            return len(self.function) > 0
        if len(self.operand_left) > 0 \
                and len(self.operator) > 0 \
                and len(self.operand_right) > 0:
            return True
        return False

    def is_function(self) -> bool:
        return len(self.function) > 0
