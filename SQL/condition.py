from SQL.variable import Variable


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
        if len(self.operand_left) > 1 \
                and len(self.operator) > 1 \
                and len(self.operand_right) > 1:
            return True
        return False

    def is_function(self) -> bool:
        return len(self.function) > 0

    def as_variable(self, obj) -> Variable:
        return obj

    def __str__(self):
        # const1    =           const2
        # t1.var1   =           t2.var1
        # t1.var1   IS NOT      NULL
        logical = self.operator_logical_previous + " " if len(self.operator_logical_previous) > 0 else ""
        left = self.as_variable(self.operand_left).to_string_condition() \
            if isinstance(self.operand_left, Variable) \
            else self.operand_left
        middle = f" {self.operator} " if len(self.operator) > 0 else ""
        right = self.as_variable(self.operand_right).to_string_condition() \
            if isinstance(self.operand_right, Variable) \
            else self.operand_right
        return logical + left + middle + right

