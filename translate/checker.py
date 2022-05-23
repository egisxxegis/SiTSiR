from typing import List

from structureMapUnpacked import StructureMapUnpacked
from translate.rdf2rdb.tripletExtended import TripletExtended


class Checker:
    def is_variable(self, variable: str) -> bool:
        # no case of $var in sp2b
        # no case of _:b1
        return len(variable) > 1 and variable.startswith("?")

    def strip_variable(self, variable: str) -> str:
        if variable.startswith("?"):
            return variable[1:]
        return variable

    def is_uri(self, uri: str) -> bool:
        return not self.is_variable(uri)

    def is_as_column_unsafe(self, predicate: str, table_name: str, the_map: StructureMapUnpacked) -> bool:
        if table_name == "":
            return False
        predicate = the_map.get_property_unsafe(predicate)
        tables_arr = the_map.property_map_tables_arr.get(predicate)
        tables_arr = [] if tables_arr is None else tables_arr
        return table_name in tables_arr

    def is_all_triplets_mapped(self, triplets_ext_arr: List[TripletExtended]) -> bool:
        for triplet_ext in triplets_ext_arr:
            if triplet_ext.table_subject == "":
                return False
        return True
