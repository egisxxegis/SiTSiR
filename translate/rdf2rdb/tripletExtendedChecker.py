from typing import List

from structureMapUnpacked import StructureMapUnpacked
from translate.rdf2rdb.tripletExtended import TripletExtended
from translate.rdf2rdb.tripletExtendedType import TripletExtendedType


class TripletExtendedChecker(object):
    def __init__(self):
        pass

    @staticmethod
    def is_tp_ext_resolved(triplet_extended: TripletExtended, rdf2rdb: StructureMapUnpacked) -> bool:
        if triplet_extended.table_subject == "":
            # no root known
            return False
        if triplet_extended.table_linking == "" \
            and not rdf2rdb.is_property_in_table(rdf2rdb.get_property_unsafe(triplet_extended.predicate),
                                                 triplet_extended.table_subject):
            # missing linking
            return False
        return True

    @staticmethod
    def is_tps_ext_arr_resolved(tps_ext_arr: List[TripletExtended], rdf2rdb: StructureMapUnpacked) -> bool:
        for tp_ext in tps_ext_arr:
            if not TripletExtendedChecker.is_tp_ext_resolved(tp_ext, rdf2rdb):
                return False
        return True
