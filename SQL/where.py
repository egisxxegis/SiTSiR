from typing import List

from SQL.condition import Condition
from SQL.reservedWords import ReservedWords


class Where:
    def __init__(self):
        self.conditions_arr: List[Condition] = []

    def condition_add(self, logical_previous_operator: str, left: str, operator: str, right: str) -> Condition:
        condition = Condition()
        condition.operand_left = left
        condition.operand_right = right
        condition.operator = operator
        if len(self.conditions_arr) > 0:
            condition.operator_logical_previous = logical_previous_operator
        self.conditions_arr.append(condition)
        return condition

    def and_condition_add(self, left: str, operator: str, right: str) -> Condition:
        return self.condition_add(ReservedWords.AND, left, operator, right)

    def or_condition_add(self, left: str, operator: str, right: str) -> Condition:
        return self.condition_add(ReservedWords.OR, left, operator, right)

    def conditions_to_str(self) -> str:
        conditions_joined = " \n".join(condition.__str__() for condition in self.conditions_arr)
        conditions_joined = "1" if len(conditions_joined) == 0 else conditions_joined
        return conditions_joined

    def get_packed_conditions(self) -> List[str]:
        conditions_joined = self.conditions_to_str()
        if len(conditions_joined) < 1:
            raise Exception("No conditions to pack")
        return ["(", conditions_joined, ")"]

    def __str__(self):
        conditions_joined = self.conditions_to_str()
        return f"WHERE {conditions_joined}"
