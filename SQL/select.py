from typing import List, Dict
from SQL.variable import Variable


class Select:
    def __init__(self):
        self.variables_arr: List[Variable] = []
        self.header_columns_arr: List[str] = []
        self.name_map_variable: Dict[str, Variable] = dict()
        self.rename_map_variable: Dict[str, Variable] = dict()
        self.is_distinct = False
        self.table_names_arr: List[str] = []
        self.table_renames_arr: List[str] = []
        self.rename_map_table: Dict[str, str] = dict()
        self.query_from_as_string = ""
        self.query_from_as_string_rename = ""

    def variable_add(self, name_or_col: str, table_rename: str, variable_rename="") -> None:
        variable = Variable(name_or_col)
        variable.table_rename = table_rename
        variable.rename = variable_rename
        self.variables_arr.append(variable)
        self.name_map_variable[name_or_col] = variable
        self.header_columns_arr.append(variable_rename if len(variable_rename) > 0 else name_or_col)
        self.rename_map_variable[self.header_columns_arr[-1]] = variable

    def function_as_variable_add(self, function_name: str, rename_as_col: str, arguments: []) -> None:
        args = ", ".join([str(arg) for arg in arguments])
        function_string = f"{function_name}({args})"
        variable = Variable(function_string)
        variable.rename = rename_as_col
        variable.is_function = True
        self.variables_arr.append(variable)
        self.name_map_variable[function_name] = variable
        self.header_columns_arr.append(rename_as_col)

    def table_add(self, table_name: str, table_rename="") -> None:
        self.table_names_arr.append(table_name)
        table_rename = table_name if table_rename == "" else table_rename
        self.rename_map_table[table_rename] = table_name
        self.table_renames_arr.append(table_rename)

    def set_from_query_as_table(self, query_as_str: str, rename_to: str) -> None:
        self.query_from_as_string = str(query_as_str)
        self.query_from_as_string_rename = rename_to
        pass

    # unused
    def is_variable_included(self, col_name: str) -> bool:
        for name in self.name_map_variable.keys():
            if name == col_name:
                return True
        return False

    # unused
    def is_only_variables(self) -> bool:
        return len(self.name_map_variable) == len(self.variables_arr)

    def is_to_use_query_in_from_clause(self, ) -> bool:
        if self.query_from_as_string == "":
            return False
        return True

    def source_as_string(self) -> str:
        if self.is_to_use_query_in_from_clause():
            return f"({self.query_from_as_string}) AS {self.query_from_as_string_rename}"
        table_rename_suffix = f" AS {self.table_renames_arr[0]}" if len(self.table_renames_arr) > 0 else ""
        return f"{self.table_names_arr[0]}{table_rename_suffix}"

    def __str__(self):
        variables_arr = [var.to_string_select() for var in self.variables_arr]
        variables_joined = ", \n".join(variables_arr)
        distinct = "DISTINCT " if self.is_distinct else ""
        source = self.source_as_string()
        return f"SELECT {distinct}{variables_joined} \nFROM {source}"
