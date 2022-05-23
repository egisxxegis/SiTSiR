class Variable:
    def __init__(self, variable_col_name: str):
        self.name = variable_col_name
        self.rename = ""
        self.table_rename = ""
        self.is_function = False

    def pack_name(self) -> str:
        return f"`{self.name}`" \
            if " " in self.name and not self.is_function \
            else self.name

    def to_string_select(self) -> str:
        name = self.pack_name()
        if len(self.rename) > 1:
            if len(self.table_rename) > 1:
                return f"{self.table_rename}.{name} as \"{self.rename}\""
            return f"{name} as \"{self.rename}\""
        if len(self.table_rename) > 1:
            return f"{self.table_rename}.{name}"
        return f"{name}"

    def to_string_condition(self) -> str:
        name = self.pack_name()
        if len(self.table_rename) > 1:
            return f"{self.table_rename}.{name}"
        return f"{name}"

    def to_string_column_final(self) -> str:
        if len(self.rename) > 0:
            return self.rename
        return self.name

    def to_string_column_current(self) -> str:
        name = self.pack_name()
        if len(self.table_rename) > 0:
            return f"{self.table_rename}.{name}"
        return name

    def __str__(self):
        return self.to_string_column_current()
