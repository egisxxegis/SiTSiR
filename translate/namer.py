import random

from SQL.reservedWords import ReservedWords
from translate.checker import Checker
import string


class Namer:
    def __init__(self):
        self.variable_map_name = dict()
        self.names_set = set()
        self.checker = Checker()

    def make_unregistered_unique(self, current_string: str) -> str:
        while True:
            new_name = current_string + "_" + ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            if new_name in self.names_set or \
                    new_name.upper() in ReservedWords.set:
                continue
            return new_name

    def register_name(self, name: str) -> None:
        self.names_set.add(name)

    def get_name(self, variable_sparql: str) -> str:
        if self.variable_map_name.get(variable_sparql) is not None:
            return self.variable_map_name[variable_sparql]

        stripped_name = self.checker.strip_variable(variable_sparql)
        new_name = stripped_name
        if new_name in self.names_set or \
                new_name in ReservedWords.set:
            new_name = self.make_unregistered_unique(stripped_name)
        self.register_name(new_name)
        self.variable_map_name[variable_sparql] = new_name
        return new_name

    def get_name_prefixed(self, variable_sparql: str, prefix: str, joining_str=".") -> str:
        return prefix + joining_str + self.get_name(variable_sparql)

    def get_string_prefixed(self, string_right: str, prefix: str, joining_str=".") -> str:
        return prefix + joining_str + string_right

    def rename(self, variable_sparql: str) -> str:
        self.get_name(variable_sparql)
        stripped = self.checker.strip_variable(variable_sparql)
        name_new = self.make_unregistered_unique(stripped)
        self.register_name(name_new)
        return name_new
