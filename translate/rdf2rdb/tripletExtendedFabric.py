from typing import Tuple, List

from structureMapUnpacked import StructureMapUnpacked
from SPARQL.triplet import Triplet
from translate.rdf2rdb.tripletExtended import TripletExtended
from SPARQL.const import Const
from translate.checker import Checker
from translate.rdf2rdb.tripletExtendedType import TripletExtendedType
from const import Const as MapConst
from translate.rdf2rdb.artificialQuery import ArtificialQuery


class TripletExtendedFabric:
    def __init__(self, rdf2rdb: StructureMapUnpacked):
        self.rdf2rdb = rdf2rdb
        self.checker = Checker()
        self.subjects_arr_tpl: List[Tuple[str, int]] = []
        self.predicates_arr_tpl: List[Tuple[str, int]] = []
        self.objects_arr_tpl: List[Tuple[str, int]] = []
        self.triplets_arr: List[Triplet] = []

    def find_type(self, triplet_ext: [TripletExtended]) -> TripletExtendedType:
        spo_stamp = [self.checker.is_variable(triplet_ext.subject),
                     self.checker.is_variable(triplet_ext.predicate),
                     self.checker.is_variable(triplet_ext.object)]
        # like a binary number. Zero is 000, Five is 101, Seven is 111
        spo_enum_value = spo_stamp[0] * 4 + spo_stamp[1] * 2 + spo_stamp[2] * 1
        return TripletExtendedType(spo_enum_value)

    @staticmethod
    def tpl_value(tpl: Tuple[str, int]) -> str:
        return tpl[0]

    @staticmethod
    def tpl_reference(tpl: Tuple[str, int]) -> int:
        return tpl[1]

    def set_triplets_arr(self, triplets_arr: List[Triplet]) -> None:
        self.subjects_arr_tpl = [(triplets_arr[i].subject, i) for i in range(0, len(triplets_arr))]
        self.predicates_arr_tpl = [(triplets_arr[i].predicate, i) for i in range(0, len(triplets_arr))]
        self.objects_arr_tpl = [(triplets_arr[i].object, i) for i in range(0, len(triplets_arr))]
        self.triplets_arr = triplets_arr

        self.subjects_arr_tpl.sort(key=self.tpl_value)
        self.predicates_arr_tpl.sort(key=self.tpl_value)
        self.objects_arr_tpl.sort(key=self.tpl_value)

    def convert_triplet_arr_to_extended_arr(self, triplets_arr: [Triplet]) -> [TripletExtended]:
        value = self.tpl_value
        reference = self.tpl_reference
        triplets_ext_arr = []
        for triplet in triplets_arr:
            triplet_ext = TripletExtended(triplet)
            triplets_ext_arr.append(triplet_ext)

        self.set_triplets_arr(triplets_arr)
        subjects_arr_tpl = self.subjects_arr_tpl
        predicates_arr_tpl = self.predicates_arr_tpl
        objects_arr_tpl = self.objects_arr_tpl

        # get roots
        triplet_roots_arr = []
        for predicate_tpl in predicates_arr_tpl:
            if value(predicate_tpl) == Const.rdfType:
                triplet_roots_arr.append(triplets_ext_arr[reference(predicate_tpl)])
            elif value(predicate_tpl) == Const.rdfsSubClassOf:
                raise Exception("rdfs:subClassOf information is not preserved in rdf2rdb. Query can not be translated")

        # set basic table names
        for triplet_root in triplet_roots_arr:
            triplet_root.is_root = True
            # indirect connection
            if self.checker.is_variable(triplet_root.object):
                raise Exception("RDF2RDB can not answer queries with rdf:type and variable object")
            # direct connection
            else:
                table = self.rdf2rdb.uri_map_table.get(triplet_root.object)
                if table is None:
                    raise Exception(f"No individuals of class {triplet_root.object} exists.")
                triplet_root.table_subject = table

            # no case of blank nodes
            if self.checker.is_uri(triplet_root.subject):
                continue

            # link same subject
            is_found_anything = False
            for subject_tpl in subjects_arr_tpl:
                if value(subject_tpl) != triplet_root.subject:
                    if is_found_anything:
                        break
                    else:
                        continue
                is_found_anything = True
                triplets_ext_arr[reference(subject_tpl)].table_subject = triplet_root.table_subject

        # Get to know triplet type

        for triplet in triplets_ext_arr:
            triplet.type = self.find_type(triplet)

        # link linking triplets
        # ?person a "Person"             Person
        # ?journal qq:writtenBy ?person  Journal_writtenby_Person
        # ?journal a "Journal"           Journal
        #
        # triplet. table subject; already set to Person
        # triplet. table linking = Journal_writtenby_Person
        # triplet. table object Journal

        # simple case -> chain

        def set_linking_table(var: str) -> bool:
            # representative found
            is_sub_repr_found = False
            is_obj_repr_found = False
            sub_reprs_arr: List[TripletExtended] = []
            obj_reprs_arr: List[TripletExtended] = []
            # all of them might not have table set (verb)
            # ?document creator ?person
            # ?person name ?name
            # but might not be
            # ?person rdf:type person:type
            for sub_tpl in subjects_arr_tpl:
                if value(sub_tpl) == var:
                    is_sub_repr_found = True
                    sub_reprs_arr.append(triplets_ext_arr[reference(sub_tpl)])
                    break
            # basically linking entries
            # ?document writtenby ?person
            # ?house builtby ?person
            for obj_tpl in objects_arr_tpl:
                if value(obj_tpl) == var:
                    is_obj_repr_found = True
                    obj_reprs_arr.append(triplets_ext_arr[reference(obj_tpl)])
                elif is_obj_repr_found:
                    break
            if not is_obj_repr_found:
                raise Exception("Query seems too ambigous: asking for subjects that are not referenced by triplets")

            # find linking tables
            linking = dict()

            # linking found. Update subject representatives' table_subject
            def update_subject_reprs_with_remove() -> bool:
                if not is_sub_repr_found:
                    # reference to other class is only uri
                    # ?document creator ?person
                    # but no
                    # ?person rdf:type type:person
                    return False
                to_remove = []
                for tpext in sub_reprs_arr:
                    # not set
                    if len(tpext.table_subject) < 1:
                        tpext.table_subject = linking[MapConst.linkingObject]
                        to_remove.append(tpext)
                        continue
                    # set incorrectly
                    if tpext.table_subject != linking[MapConst.linkingObject]:
                        raise Exception(f"Linking failed! {tpext}. \n"
                                        f"Says it is in {tpext.table_subject} \n"
                                        f"but linking {linking[MapConst.linkingTable]} says, "
                                        f"it belongs to f{linking[MapConst.linkingObject]}")
                    # set correctly
                    else:
                        # we will only mark them for removing
                        to_remove.append(tpext)
                if len(to_remove) > 0:
                    for remove in to_remove:
                        sub_reprs_arr.remove(remove)
                    return True
                return False

            # iterate through obj_reprs
            # while atleast any update occurs
            is_updated = False
            to_remove_obj = []
            while True:
                for tp_ext in obj_reprs_arr:
                    if len(tp_ext.table_subject) < 1:
                        # ?unknownType references ?person
                        # maybe it is unknownType just for now
                        continue
                        # moved to after check
                        # raise NotImplementedError(tp_ext)
                    if self.checker.is_variable(tp_ext.predicate):
                        # ?document ?referenceProp ?person
                        # or (etc.)
                        # ?document ?referenceProp personUri
                        raise NotImplementedError(tp_ext)
                    possible_linkings = self.rdf2rdb.get_possible_linkings_sp_arr(tp_ext.table_subject,
                                                                                  tp_ext.predicate)
                    if len(possible_linkings) == 0:
                        if self.checker.is_as_column_unsafe(tp_ext.predicate, tp_ext.table_subject, self.rdf2rdb):
                            is_updated = update_subject_reprs_with_remove()
                            to_remove_obj.append(tp_ext)
                            break
                        raise Exception(f"Linking not found for triplet {tp_ext}. "
                                        f"Subject table: {tp_ext.table_subject}")
                    if len(possible_linkings) > 1:
                        raise NotImplementedError(tp_ext)
                    linking = possible_linkings[0]
                    is_updated_self = tp_ext.table_linking == ""
                    tp_ext.table_linking = linking[MapConst.linkingTable]
                    tp_ext.table_object = linking[MapConst.linkingObject]
                    is_updated = update_subject_reprs_with_remove() or is_updated_self
                    to_remove_obj.append(tp_ext)
                    break
                if len(to_remove_obj) > 0:
                    for remove_obj in to_remove_obj:
                        obj_reprs_arr.remove(remove_obj)
                    to_remove_obj.clear()
                if is_updated:
                    is_updated = False
                    continue
                else:
                    if len(obj_reprs_arr) > 0:
                        if len(obj_reprs_arr[0].table_subject) < 1:
                            # ?unknownType references ?person
                            # raise NotImplementedError(obj_reprs_arr[0])
                            return False
                        else:
                            raise Exception(f"Could not process {obj_reprs_arr[0]} in linking process")
                    return True
            pass

        subjects_var_set = set()
        objects_var_set = set()
        # only full chain satisfies.
        # ?inproc creator ?person
        # ?person prop obj
        for triplet in triplets_ext_arr:
            subjects_var_set.add(triplet.subject)
            objects_var_set.add(triplet.object)
        # support for half chain.
        # ?inproc creator ?person
        # but no
        # ?person prop obj
        for tp in triplets_ext_arr:
            # it can not be object-property
            if tp.type not in [TripletExtendedType.VAR_SO, TripletExtendedType.VAR_OBJECT]:
                continue
            # it is already mentioned
            if tp.object in subjects_var_set:
                continue
            # it is column-property
            tables_arr = self.rdf2rdb.property_map_tables_arr.get(self.rdf2rdb.get_property_unsafe(tp.predicate))
            tables_arr = [] if tables_arr is None else tables_arr
            if tp.table_subject in tables_arr:
                continue
            # it is half chain
            subjects_var_set.add(tp.object)
        # find linkings
        is_it_updated = False
        to_remove_subject = []
        while True:
            for subject in subjects_var_set:
                if subject in objects_var_set:
                    if set_linking_table(subject):
                        is_it_updated = True
                        to_remove_subject.append(subject)
                        break
                    continue
            if len(to_remove_subject) > 0:
                for remove_subject in to_remove_subject:
                    subjects_var_set.remove(remove_subject)
                to_remove_subject.clear()
            if is_it_updated:
                is_it_updated = False
                continue
            else:
                break

        for triplet in triplets_ext_arr:
            triplet.artificial_type = ArtificialQuery.find_type(triplet)

        return triplets_ext_arr
