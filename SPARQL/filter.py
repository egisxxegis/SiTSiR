from SPARQL.conditon import Condition
from typing import List


class Filter:
    def __init__(self):
        self.condition_temp: Condition = Condition()
        self.conditions_arr: List[Condition] = []
        pass

    def is_condition_existant(self) -> bool:
        return len(self.conditions_arr) > 0

    def create_condition(self) -> None:
        self.condition_temp = Condition()
        self.conditions_arr.append(self.condition_temp)
