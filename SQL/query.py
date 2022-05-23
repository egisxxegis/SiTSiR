from typing import List

from SQL.joinType import JoinType
from SQL.select import Select
from SQL.order import Order
from SQL.where import Where
from SQL.join import Join
from SQL.union import Union


class Query:
    def __init__(self):
        self.select = Select()
        self.order = Order()
        self.where = Where()
        self.joins_arr: List[Join] = []
        self.union: Union = Union()
        self.is_union_set = False

        self.limit = -1
        self.offset = -1

    def join_add(self, table_root: str, table_branch: str, join_type: JoinType,
                 table_branch_rename="", col_root_id="", col_branch_id="") -> None:
        join = Join(table_root, table_branch)
        if len(table_branch_rename) > 0:
            join.table_to_be_joined_rename = table_branch_rename
        if len(col_root_id) > 0 \
                or len(col_branch_id) > 0:
            join.set_columns(col_root_id, col_branch_id)
        join.type = join_type
        self.joins_arr.append(join)

    def join_add_from_query_str(self, source_root: str,
                                query_as_str: str,
                                join_type: JoinType,
                                query_rename="") -> None:
        self.join_add(source_root, f"({query_as_str})", join_type, query_rename)

    def union_set(self, select: Select, where: Where, joins_arr: List[Join]) -> Union:
        self.union.select = select
        self.union.where = where
        self.union.joins_arr = [join for join in joins_arr]
        self.is_union_set = True
        return self.union

    @staticmethod
    def to_string(select: Select, where: Where, joins_arr: List[Join]) -> str:
        if len(joins_arr) < 1:
            return f"{select}\n{where}"
        join_string = "\n".join([join.__str__() for join in joins_arr])
        return f"{select}\n{join_string}\n{where}"

    def __str__(self):
        query = self.to_string(self.select, self.where, self.joins_arr)
        union_suffix = " \nUNION \n" + self.to_string(self.union.select, self.union.where, self.union.joins_arr) \
            if self.is_union_set \
            else ""
        order_suffix = f" \n{self.order}" if len(self.order.variables_arr) > 0 else ""
        limit_suffix = f" \nLIMIT {self.limit}" if self.limit > -1 else ""
        offset_suffix = f" \nOFFSET {self.offset}" if self.offset > -1 else ""
        return f"{query}{union_suffix}{order_suffix}{limit_suffix}{offset_suffix}"
