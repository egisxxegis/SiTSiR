from typing import List, Dict

from SPARQL.query import Query
from SQL.joinType import JoinType
from structureMapUnpacked import StructureMapUnpacked
from SPARQL.triplet import Triplet
from translate.checker import Checker
from translate.queryComparator import QueryComparator
from translate.rdf2rdb.tripletExtendedFabric import TripletExtendedFabric
from translate.rdf2rdb.tripletExtended import TripletExtended
from translate.rdf2rdb.tripletExtendedArrUtils import TripletExtendedArrUtils
from translate.rdf2rdb.tripletExtendedMemory import TripletExtendedMemory
from translate.rdf2rdb.tripletExtendedType import TripletExtendedType as TpType
from SQL.query import Query as QuerySQL
from SQL.variable import Variable
from translate.namer import Namer
from const import Const
from SQL.where import Where
from translate.graphTraveler import GraphTraveler
from translate.rdf2rdb.tripletExtendedChecker import TripletExtendedChecker


class ArtificialQuery:
    def __init__(self):
        pass

    @staticmethod
    def get_q_known_class_spo(var_namer: Namer,
                              triplet: TripletExtended,
                              rdf2rdb: StructureMapUnpacked) -> QuerySQL:
        if triplet.table_subject == "":
            raise Exception(f"Called artificial SPO method but no table_subject is known for triplet: {triplet}")

        props_all_arr = rdf2rdb.property_map_tables_arr.keys()
        props_arr = []
        for prop in props_all_arr:
            if triplet.table_subject in rdf2rdb.property_map_tables_arr[prop]:
                props_arr.append(prop)

        linkings_arr = []
        for linking in rdf2rdb.linking_tables_arr_dict:
            if linking[Const.linkingSubject] == triplet.table_subject:
                linkings_arr.append(linking)

        tbl_namer = Namer()

        query_partials_arr = []

        # PURE PROPERTY
        # property value might not be presented, therefore we need "IS NOT NULL" check
        for prop in props_arr:
            uris_arr = rdf2rdb.get_possible_prop_uris_arr(prop)
            if len(uris_arr) == 0:
                raise Exception(f"Could not find URI for property {prop} of table {triplet.table_subject}")
            if len(uris_arr) > 1:
                raise NotImplementedError

            sql = QuerySQL()
            sql.select.variable_add(rdf2rdb.meta[Const.metaColUris], "", var_namer.get_name(triplet.subject))
            sql.select.variable_add(f'"{uris_arr[0]}"', "", var_namer.get_name(triplet.predicate))
            sql.select.table_add(triplet.table_subject)
            sql.select.variable_add(prop, triplet.table_subject, var_namer.get_name(triplet.object))
            sql.where.and_condition_add(var_namer.get_name_prefixed(prop, triplet.table_subject),
                                        Const.opIsNot,
                                        Const.null)
            query_partials_arr.append(sql)

        # OBJECT PROPERTY
        # uri is always present, therefore no "IS NOT NULL" check is needed
        for linking in linkings_arr:
            uris_arr = rdf2rdb.get_possible_prop_uris_arr(linking[Const.linkingPredicate])
            if len(uris_arr) == 0:
                uris_arr = [linking[Const.linkingPredicate]]
                print(f"FAKING replacement. Could not find URI for property {linking[Const.linkingPredicate]} "
                      f"of table {triplet.table_subject}")
                # raise Exception(f"Could not find URI for property {linking[Const.linkingPredicate]} "
                #                 f"of table {triplet.table_subject}")
            if len(uris_arr) > 1:
                raise NotImplementedError

            table_linking = linking[Const.linkingTable]
            table_object = linking[Const.linkingObject]

            renamed_table = tbl_namer.rename(linking[Const.linkingSubject])
            renamed_linking_table = tbl_namer.rename(table_linking)
            renamed_table_object = tbl_namer.rename(table_object)

            col_root_id1 = rdf2rdb.get_col_id(linking[Const.linkingSubject])
            col_root_id2 = rdf2rdb.get_col_id(table_object)
            col_linking_id1 = col_root_id1 + "1"
            col_linking_id2 = col_root_id2 + "2"

            sql = QuerySQL()

            sql.join_add(renamed_table,
                         table_linking,
                         JoinType.INNER,
                         renamed_linking_table,
                         col_root_id1,
                         col_linking_id1)
            sql.join_add(renamed_linking_table,
                         table_object,
                         JoinType.INNER,
                         renamed_table_object,
                         col_linking_id2,
                         col_root_id2)

            sql.select.variable_add(rdf2rdb.meta[Const.metaColUris], renamed_table, var_namer.get_name(triplet.subject))
            sql.select.variable_add(f'"{uris_arr[0]}"', "", var_namer.get_name(triplet.predicate))
            sql.select.table_add(triplet.table_subject, renamed_table)

            sql.select.variable_add(rdf2rdb.meta[Const.metaColUris],
                                    renamed_table_object,
                                    var_namer.get_name(triplet.object))
            sql.select.table_add(table_linking, renamed_linking_table)
            sql.select.table_add(table_object, renamed_table_object)

            query_partials_arr.append(sql)

        unioned = " \nUNION \n".join([str(q) for q in query_partials_arr])

        arti_name = tbl_namer.rename("artificial")
        sql = QuerySQL()
        sql.select.set_from_query_as_table(unioned, arti_name)
        sql.select.variable_add(var_namer.get_name(triplet.subject), arti_name)
        sql.select.variable_add(var_namer.get_name(triplet.predicate), arti_name)
        sql.select.variable_add(var_namer.get_name(triplet.object), arti_name)

        return sql
