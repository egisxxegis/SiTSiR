from SQL.variable import Variable
from typing import List


class Order:
    def __init__(self):
        self.variables_arr: List[Variable] = []

    def __str__(self):
        if len(self.variables_arr) < 1:
            return ""
        order_by_joined = ", ".join([var.to_string_condition() for var in self.variables_arr])
        return f"ORDER BY {order_by_joined}"
