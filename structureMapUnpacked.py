import yaml
from typing import List, Dict
from const import Const


class StructureMapUnpacked(yaml.YAMLObject):
    yaml_tag = u'!StructureMapUnpacked'

    def __init__(self):
        self.uri_map_table: Dict[str, str] = dict()
        self.uri_map_property: Dict[str, str] = dict()
        self.property_map_tables_arr: Dict[str, List[str]] = dict()
        self.class_tables_arr: List[str] = []
        self.linking_tables_arr_dict: List[Dict[str, str]] = []

        self.meta: Dict[str, str] = dict()

    @staticmethod
    def uri_to_property_unsafe(uri: str) -> str:
        hash_index = uri.rfind("#")
        slash_index = uri.rfind("/")
        return uri[max(hash_index, slash_index) + 1:].lower()

    def get_property_unsafe(self, uri: str) -> str:
        prop = self.uri_map_property.get(uri)
        if prop is None:
            prop = self.uri_to_property_unsafe(uri)
        return prop

    def is_property_in_table(self, prop: str, table: str) -> bool:
        tables_arr = self.property_map_tables_arr.get(prop)
        if tables_arr is None:
            return False
        return table in tables_arr

    def get_possible_linkings_sp_arr(self, s_table: str, prop_uri: str) -> List[Dict[str, str]]:
        prop_uri = self.get_property_unsafe(prop_uri)
        to_return = []
        for linking in self.linking_tables_arr_dict:
            if linking[Const.linkingPredicate] == prop_uri \
                    and linking[Const.linkingSubject] == s_table:
                to_return.append(linking)
        return to_return

    def get_possible_linkings_spo_arr(self, s_table: str, prop_uri: str, o_table: str) -> List[Dict[str, str]]:
        prop_uri = self.get_property_unsafe(prop_uri)
        not_found = []
        for linking in self.linking_tables_arr_dict:
            if linking[Const.linkingPredicate] == prop_uri \
                    and linking[Const.linkingSubject] == s_table \
                    and linking[Const.linkingObject] == o_table:
                return [linking]
        return not_found

    def get_col_id(self, s_table: str) -> str:
        prefix = self.meta[Const.metaColIdPrefix]
        suffix = self.meta[Const.metaColIdSuffix]
        return f"{prefix}{s_table}{suffix}"

    def get_possible_prop_uris_arr(self, prop: str) -> List[str]:
        to_return = []
        for uri, p_short in self.uri_map_property.items():
            if p_short == prop:
                to_return.append(uri)
        return to_return
