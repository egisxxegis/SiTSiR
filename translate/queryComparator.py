from typing import List, Set

from SQL.query import Query


class QueryComparator:
    def __init__(self, query1: Query, query2: Query):
        self.q1 = query1
        self.q2 = query2
        self.q1_cols_arr: List[str] = [col for col in self.q1.select.header_columns_arr]
        self.q2_cols_arr: List[str] = [col for col in self.q2.select.header_columns_arr]
        self.q1_cols_set = set(self.q1_cols_arr)
        self.q2_cols_set = set(self.q2_cols_arr)
        self.q1_intersection_q2_set = self.q1_cols_set.intersection(self.q2_cols_set)

    def intersection(self) -> List[str]:
        return list(self.q1_intersection_q2_set)

    def q1_minus_q2(self) -> List[str]:
        return [col for col in self.q1_cols_arr if col not in self.q1_intersection_q2_set]

    def q2_minus_q1(self) -> List[str]:
        return [col for col in self.q2_cols_arr if col not in self.q1_intersection_q2_set]
