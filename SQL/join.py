from SQL.joinType import JoinType
from const import Const
from SQL.where import Where


class Join:
    def __init__(self, table_root_renamed: str, table_to_be_joined: str, table_to_be_joined_rename=""):
        self.type = JoinType.UNKNOWN
        self.table_root_renamed = table_root_renamed
        self.table_to_be_joined = table_to_be_joined
        self.table_to_be_joined_rename = "" if len(table_to_be_joined_rename) < 1 else table_to_be_joined_rename
        self.col_root = ""
        self.col_joined = ""
        self.is_to_use_col_names = False
        self.where_as_conditions = Where()
        self.is_to_use_where_as_conditions = False
        self.is_join_on_false = False

    def set_columns(self, col_root: str, col_joined: str) -> None:
        self.col_root = col_root
        self.col_joined = col_joined
        self.is_to_use_col_names = True

    def set_on_clause(self, where_as_conditions: Where) -> None:
        self.where_as_conditions = where_as_conditions
        self.is_to_use_where_as_conditions = True

    def __str__(self):
        join_string = "UNKNOWN JOIN"
        if self.type == JoinType.LEFT:
            join_string = "LEFT OUTER JOIN"
        elif self.type == JoinType.INNER:
            join_string = "INNER JOIN"

        join_table = self.table_to_be_joined

        suffix_as = f" AS {self.table_to_be_joined_rename}" if len(self.table_to_be_joined_rename) > 1 else ""
        suffix_on = " \nON 0" if self.is_join_on_false else " \nON 1"
        if self.is_to_use_col_names:
            join_table_final_name = self.table_to_be_joined_rename if len(self.table_to_be_joined_rename) > 0 \
                else join_table
            suffix_on += f" \nAND {self.table_root_renamed}.{self.col_root}" \
                         f" {Const.opEqual} " \
                         f"{join_table_final_name}.{self.col_joined}"
        if self.is_to_use_where_as_conditions:
            suffix_on += " \nAND " + self.where_as_conditions.conditions_to_str()

        return f"{join_string} {self.table_to_be_joined}{suffix_as}{suffix_on}"

