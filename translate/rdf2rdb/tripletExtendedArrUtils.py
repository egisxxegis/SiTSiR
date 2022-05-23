from typing import List, Dict

from structureMapUnpacked import StructureMapUnpacked
from translate.checker import Checker
from translate.rdf2rdb.tripletExtended import TripletExtended
from translate.rdf2rdb.tripletExtendedChecker import TripletExtendedChecker as TpExtChecker
from translate.rdf2rdb.tripletExtendedFabric import TripletExtendedFabric
from const import Const


class TripletExtendedArrUtils:
    def __init__(self, triplets_extended_arr: List[TripletExtended]):
        self.triplets_ext_arr: List[TripletExtended] = triplets_extended_arr
        self.subjects_arr: List[str] = []
        self.predicates_arr: List[str] = []
        self.objects_arr: List[str] = []
        self.checker = Checker()

    def sort(self) -> None:
        def get_table(triplet: TripletExtended) -> str:
            return triplet.table_subject
        self.triplets_ext_arr.sort(key=get_table)

        def find_table_end_index(start: int, table_name: str) -> int:
            the_i = 0
            for the_i in range(start, len(self.triplets_ext_arr)):
                if self.triplets_ext_arr[the_i].table_subject == table_name:
                    continue
                the_i -= 1
                break
            return the_i

        def find_swappable_index(start: int, i_table_last: int) -> int:
            the_i = start
            for the_i in range(i_table_last, start - 1, -1):
                if self.triplets_ext_arr[the_i].is_linking():
                    continue
                break
            return the_i

        i_table_end = 0
        for i in range(len(self.triplets_ext_arr)):
            if i_table_end == 0 or i_table_end < i:
                table = self.triplets_ext_arr[i].table_subject
                i_table_end = find_table_end_index(i, table)
            if self.triplets_ext_arr[i].is_linking():
                # SWAP to bottom
                i_swap = find_swappable_index(i, i_table_end)
                if i == i_swap:
                    continue
                self.triplets_ext_arr[i], self.triplets_ext_arr[i_swap] = \
                    self.triplets_ext_arr[i_swap], self.triplets_ext_arr[i]

    def get_subjects_arr(self) -> List[str]:
        if len(self.subjects_arr) == 0:
            self.subjects_arr = [tp.subject for tp in self.triplets_ext_arr]
        return self.subjects_arr

    def get_predicates_arr(self) -> List[str]:
        if len(self.predicates_arr) == 0:
            self.predicates_arr = [tp.predicate for tp in self.triplets_ext_arr]
        return self.predicates_arr

    def get_objects_arr(self) -> List[str]:
        if len(self.objects_arr) == 0:
            self.objects_arr = [tp.object for tp in self.triplets_ext_arr]
        return self.objects_arr

    def get_split_into_subject_partitions(self) -> List[List[TripletExtended]]:
        subject_map_index: Dict[str, int] = dict()
        triplets_arr_arr: List[List[TripletExtended]] = []
        for triplet in self.triplets_ext_arr:
            if self.checker.is_uri(triplet.subject):
                raise NotImplementedError
            if subject_map_index.get(triplet.subject) is None:
                subject_map_index[triplet.subject] = len(triplets_arr_arr)
                triplets_arr_arr.append(list())
            triplets_arr_arr[subject_map_index[triplet.subject]].append(triplet)
        return triplets_arr_arr

    def update_as_extension_of(self, triplets_ext_arr: List[TripletExtended], rdf2rdb: StructureMapUnpacked):
        tp_ext_fabric = TripletExtendedFabric(rdf2rdb)
        tps_unresolved_arr = [tp for tp in self.triplets_ext_arr]
        tps_resolved_arr: List[TripletExtended] = []

        def update_resolved_unresolved() -> None:
            _to_move_arr = []
            for tp in tps_unresolved_arr:
                if TpExtChecker.is_tp_ext_resolved(tp, rdf2rdb):
                    _to_move_arr.append(tp)
            for tp in _to_move_arr:
                tps_unresolved_arr.remove(tp)
                tps_resolved_arr.append(tp)
            return

        def find_base_roots_dict(tps_arr: List[TripletExtended]) -> Dict[str, str]:
            _var_map_table_subject = dict()
            for tp in tps_arr:
                # ?s linking ?o
                if tp.table_linking != "" \
                        and self.checker.is_variable(tp.object):
                    _var_map_table_subject[tp.object] = tp.table_object
                # ?s prop ANY
                if tp.table_subject != "" \
                        and self.checker.is_variable(tp.subject):
                    _var_map_table_subject[tp.subject] = tp.table_subject
            return _var_map_table_subject

        def update_using_roots(var_map_table: Dict[str, str], tps_arr: List[TripletExtended]) -> None:
            for tp in tps_arr:
                _table = var_map_table.get(tp.subject)
                if _table is not None:
                    tp.table_subject = _table

                _table = var_map_table.get(tp.object)
                if _table is not None:
                    tp.table_object = _table
                    pass
            return

        def update_linkings(tps_arr: List[TripletExtended], mapping: StructureMapUnpacked) -> None:
            for tp in tps_arr:
                if self.checker.is_variable(tp.predicate):
                    raise NotImplementedError
                if tp.table_subject == "":
                    continue
                if mapping.is_property_in_table(mapping.get_property_unsafe(tp.predicate), tp.table_subject):
                    continue

                mapping.get_possible_linkings_spo_arr(tp.table_subject, tp.predicate, tp.table_object)
                _linkings = mapping.get_possible_linkings_sp_arr(tp.table_subject, tp.predicate) \
                    if tp.table_object == "" \
                    else mapping.get_possible_linkings_spo_arr(tp.table_subject, tp.predicate, tp.table_object)
                if len(_linkings) == 0:
                    continue
                if len(_linkings) > 1:
                    raise NotImplementedError
                tp.table_linking = _linkings[Const.linkingTable]
                tp.table_object = _linkings[Const.linkingObject]

        def update_roots_dict(var_map_table: Dict[str, str], the_tps_unresolved_arr: List[TripletExtended]) -> None:
            for tp in the_tps_unresolved_arr:
                if self.checker.is_variable(tp.subject) \
                        and tp.table_subject != "":
                    var_map_table[tp.subject] = tp.table_subject
                if self.checker.is_variable(tp.object) \
                        and tp.table_object != "":
                    var_map_table[tp.subject] = tp.table_object
            return

        var_map_table_subject = find_base_roots_dict(triplets_ext_arr)
        iterations_max = 100
        while iterations_max > 0:
            update_resolved_unresolved()
            if len(tps_unresolved_arr) == 0:
                # no update needed
                return
            update_using_roots(var_map_table_subject, tps_unresolved_arr)
            update_linkings(tps_unresolved_arr, rdf2rdb)
            update_roots_dict(var_map_table_subject, tps_unresolved_arr)

            iterations_max -= 1
        return
