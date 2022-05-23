from typing import List, Dict

from SPARQL.query import Query
from SQL.joinType import JoinType
from structureMapUnpacked import StructureMapUnpacked
from SPARQL.triplet import Triplet
from SPARQL.const import Const as SPARQLConst
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
from translate.rdf2rdb.artificialQuery import ArtificialQuery
from SPARQL.graph import Graph


class Translator:
    def __init__(self, normalised_query: Query, rdf2rdb: StructureMapUnpacked):
        self.query = normalised_query
        self.rdf2rdb = rdf2rdb
        self.namer = Namer()
        self.checker = Checker()

    def extract_variables_all(self, triplets_ext_sorted_arr: List[TripletExtended]) -> List[Variable]:
        variables_arr = []
        variable_names_set = set()

        def add_variable_if_inexistant(variable_sparql: str, the_triplet_ext: TripletExtended) -> bool:
            the_name = self.namer.get_name(variable_sparql)
            if variable_sparql in variable_names_set:
                return False
            variable = Variable(the_name)
            variable.table_rename = the_triplet_ext.table_subject
            variable.rename = variable.name
            variables_arr.append(variable)
            variable_names_set.add(variable_sparql)
            return True

        for triplet_ext in triplets_ext_sorted_arr:
            for term in [triplet_ext.subject, triplet_ext.predicate, triplet_ext.object]:
                if self.checker.is_variable(term):
                    add_variable_if_inexistant(term, triplet_ext)

        return variables_arr

    @staticmethod
    def triplets_ext_arr_to_triplets_ext_arr_arr(
            triplets_ext_arr: List[TripletExtended]) -> List[List[TripletExtended]]:
        to_return = []
        one_table_kind_arr = []
        i = 0
        while True:
            triplet_ext = triplets_ext_arr[i]
            one_table_kind_arr.append(triplet_ext)
            if i + 1 >= len(triplets_ext_arr):
                to_return.append(one_table_kind_arr)
                break
            i += 1
            if triplets_ext_arr[i].table_subject != one_table_kind_arr[0].table_subject:
                to_return.append(one_table_kind_arr)
                one_table_kind_arr = []
        return to_return

    def translate_one_table_one_subject_triplets_arr(self,
                                                     triplets_arr: List[TripletExtended],
                                                     tbl_namer: Namer,
                                                     var_namer: Namer) -> QuerySQL:
        # basics ?var pred ?obj
        sql = QuerySQL()
        col_uri = self.rdf2rdb.meta[Const.metaColUris]
        is_rooted = False
        renamed_table = tbl_namer.rename(triplets_arr[0].table_subject)
        open_tps_arr: List[TripletExtended] = []
        subject_map_table_rename: Dict[str, str] = dict()
        for triplet in triplets_arr:
            if triplet.type in [TpType.UNKNOWN,
                                TpType.ONLY_URI,
                                TpType.VAR_OBJECT,
                                TpType.VAR_SP,
                                TpType.VAR_SPO]:
                if triplet.type == TpType.VAR_SPO and triplet.table_subject != "":
                    open_tps_arr.append(triplet)
                    continue
                raise NotImplementedError(triplet.type)
            if not is_rooted:
                sql.select.table_add(triplet.table_subject, renamed_table)
                sql.select.variable_add(col_uri, renamed_table, var_namer.get_name(triplet.subject))
                is_rooted = True
            if triplet.is_root:
                continue
            if triplet.type == TpType.VAR_SUBJECT:
                # restriction
                # ?var predicate object
                prop = self.rdf2rdb.get_property_unsafe(triplet.predicate)
                if triplet.table_subject in self.rdf2rdb.property_map_tables_arr[prop]:
                    sql.where.and_condition_add(self.namer.get_name_prefixed(prop, renamed_table),
                                                Const.opEqual,
                                                triplet.object)
                    continue
            if triplet.type == TpType.VAR_SO:
                # ?document title ?title    - select
                # OR
                # ?document creator ?person - inner join
                if triplet.is_linking():
                    renamed_linking_table = tbl_namer.rename(triplet.table_linking)
                    renamed_table_object = tbl_namer.rename(triplet.table_object)

                    col_root_id1 = self.rdf2rdb.get_col_id(triplet.table_subject)
                    col_root_id2 = self.rdf2rdb.get_col_id(triplet.table_object)
                    col_linking_id1 = col_root_id1 + "1"
                    col_linking_id2 = col_root_id2 + "2"

                    sql.join_add(renamed_table,
                                 triplet.table_linking,
                                 JoinType.INNER,
                                 renamed_linking_table,
                                 col_root_id1,
                                 col_linking_id1)
                    sql.join_add(renamed_linking_table,
                                 triplet.table_object,
                                 JoinType.INNER,
                                 renamed_table_object,
                                 col_linking_id2,
                                 col_root_id2)

                    sql.select.variable_add(self.rdf2rdb.meta[Const.metaColUris],
                                            renamed_table_object,
                                            var_namer.get_name(triplet.object))
                    sql.select.table_add(triplet.table_linking, renamed_linking_table)
                    sql.select.table_add(triplet.table_object, renamed_table_object)
                else:
                    prop = self.rdf2rdb.get_property_unsafe(triplet.predicate)
                    if sql.select.is_variable_included(prop):
                        raise NotImplementedError
                    sql.select.variable_add(prop, renamed_table, var_namer.get_name(triplet.object))
                    sql.where.and_condition_add(var_namer.get_string_prefixed(prop, renamed_table),
                                                Const.opIsNot,
                                                Const.null)

        if len(open_tps_arr) > 1:
            raise NotImplementedError
        for tp in open_tps_arr:
            if tp.type == TpType.VAR_SPO:
                sql_open = ArtificialQuery.get_q_known_class_spo(var_namer, tp, self.rdf2rdb)
            else:
                raise NotImplementedError
            sql = self.q1_and_q2(sql, sql_open, Namer())

        return sql

    def translate_one_table_triplets_arr_arr(self, triplets_arr_arr: List[List[TripletExtended]], namer: Namer)\
            -> QuerySQL:
        # get partials and then partial1 UNION partial2
        query_partials_arr = [self.translate_one_table_one_subject_triplets_arr(one_subject,
                                                                                Namer(),
                                                                                namer)
                              for one_subject in triplets_arr_arr]
        if len(query_partials_arr) == 0:
            raise Exception("Empty partial query. Translation failed")
        elif len(query_partials_arr) == 1:
            return query_partials_arr[0]
        else:
            query_root = query_partials_arr[0]
            for i in range(1, len(query_partials_arr)):
                query_root = self.q1_and_q2(query_root, query_partials_arr[i], namer)
            return query_root

    @staticmethod
    def q1_and_q2(query_sql_1: QuerySQL, query_sql_2: QuerySQL, q_namer: Namer) -> QuerySQL:
        # distinct
        # terms q1 - q2
        # terms q2 - q1
        # intersection (use COALESCE (q1.term, q2.term) for these)
        comparator = QueryComparator(query_sql_1, query_sql_2)
        q1_name = q_namer.rename("q")
        q2_name = q_namer.rename("q")
        q3 = QuerySQL()
        q3.select.set_from_query_as_table(query_sql_1, q1_name)

        for q1_exclusive in comparator.q1_minus_q2():
            q3.select.variable_add(q1_exclusive, q1_name)
        for q2_exclusive in comparator.q2_minus_q1():
            q3.select.variable_add(q2_exclusive, q2_name)

        join_on_where = Where()
        join_on_where.and_condition_add("1", "", "")

        for shared_var in comparator.intersection():
            q1_var = Variable(shared_var)
            q1_var.table_rename = q1_name
            q2_var = Variable(shared_var)
            q2_var.table_rename = q2_name

            q3.select.function_as_variable_add(Const.coalesce, shared_var, [q1_var, q2_var])

            where = Where()
            where.and_condition_add(str(q1_var), Const.opEqual, str(q2_var))
            where.or_condition_add(str(q1_var), Const.opIs, Const.null)
            where.or_condition_add(str(q2_var), Const.opIs, Const.null)

            join_on_where.and_condition_add(*where.get_packed_conditions())

        # q3.join_add(q1_name, q2_name, JoinType.INNER)
        q3.join_add_from_query_str(q1_name, str(query_sql_2), JoinType.INNER, q2_name)
        q3.joins_arr[-1].set_on_clause(join_on_where)
        q3.select.is_distinct = True
        return q3

    @staticmethod
    def q1_optional_q2(query_sql_1: QuerySQL, query_sql_2: QuerySQL, q_namer: Namer) -> QuerySQL:
        # distinct
        # terms q1 - q2
        # terms q2 - q1
        # intersection (use COALESCE (q1.term, q2.term) for these)
        comparator = QueryComparator(query_sql_1, query_sql_2)
        q1_name = q_namer.rename("q")
        q2_name = q_namer.rename("q")
        q3 = QuerySQL()
        q3.select.set_from_query_as_table(query_sql_1, q1_name)

        for q1_exclusive in comparator.q1_minus_q2():
            q3.select.variable_add(q1_exclusive, q1_name)
        for q2_exclusive in comparator.q2_minus_q1():
            q3.select.variable_add(q2_exclusive, q2_name)

        join_on_where = Where()
        join_on_where.and_condition_add("1", "", "")
        for shared_var in comparator.intersection():
            q1_var = Variable(shared_var)
            q1_var.table_rename = q1_name
            q2_var = Variable(shared_var)
            q2_var.table_rename = q2_name

            q3.select.function_as_variable_add(Const.coalesce, shared_var, [q1_var, q2_var])

            where = Where()
            where.and_condition_add(str(q1_var), Const.opEqual, str(q2_var))
            where.or_condition_add(str(q1_var), Const.opIs, Const.null)
            where.or_condition_add(str(q2_var), Const.opIs, Const.null)

            join_on_where.and_condition_add(*where.get_packed_conditions())

        # q3.join_add(q1_name, q2_name, JoinType.LEFT)
        q3.join_add_from_query_str(q1_name, str(query_sql_2), JoinType.LEFT, q2_name)
        q3.joins_arr[-1].set_on_clause(join_on_where)
        q3.select.is_distinct = True
        return q3

    @staticmethod
    def q1_union_q2(query_sql_1: QuerySQL, query_sql_2: QuerySQL, q_namer: Namer) -> QuerySQL:
        # not distinct
        # ordered terms q1 - q2
        # ordered terms q2 - q1
        # ordered terms q1 INTERSECTION q2
        comparator = QueryComparator(query_sql_1, query_sql_2)
        q1_name = q_namer.rename("q")
        q2_name = q_namer.rename("q")
        q1_as_joined_name = q_namer.rename("q")
        q2_as_joined_name = q_namer.rename("q")

        q3_union_top = QuerySQL()
        q3_union_top.select.set_from_query_as_table(query_sql_1, q1_name)
        q4_union_bottom = QuerySQL()
        q4_union_bottom.select.set_from_query_as_table(query_sql_2, q2_name)

        q1_minus_q2 = comparator.q1_minus_q2()
        q1_minus_q2.sort()
        q2_minus_q1 = comparator.q2_minus_q1()
        q2_minus_q1.sort()
        q1_intersection_q2 = comparator.intersection()
        q1_intersection_q2.sort()

        for q1_exclusive in q1_minus_q2:
            q3_union_top.select.variable_add(q1_exclusive, q1_name)
            q4_union_bottom.select.variable_add(q1_exclusive, q1_as_joined_name)
        for q2_exclusive in q2_minus_q1:
            q3_union_top.select.variable_add(q2_exclusive, q2_as_joined_name)
            q4_union_bottom.select.variable_add(q2_exclusive, q2_name)
        for shared_var in q1_intersection_q2:
            q3_union_top.select.variable_add(shared_var, q1_name)
            q4_union_bottom.select.variable_add(shared_var, q2_name)

        q3_union_top.join_add_from_query_str(str(query_sql_1), str(query_sql_2), JoinType.LEFT, q2_as_joined_name)
        q3_union_top.joins_arr[-1].is_join_on_false = True
        q4_union_bottom.join_add_from_query_str(str(query_sql_2), str(query_sql_1), JoinType.LEFT, q1_as_joined_name)
        q4_union_bottom.joins_arr[-1].is_join_on_false = True

        q3_union_top.union_set(q4_union_bottom.select, q4_union_bottom.where, q4_union_bottom.joins_arr)
        return q3_union_top

    def translate_graph_triplets_arr(self, triplets_ext_arr: List[TripletExtended]) -> QuerySQL:
        namer = Namer()

        variables_arr = self.extract_variables_all(triplets_ext_arr)
        triplets_by_table_arr = self.triplets_ext_arr_to_triplets_ext_arr_arr(triplets_ext_arr)

        triplets_by_table_subject_arr = [TripletExtendedArrUtils(tpext_arr_by_tbl).get_split_into_subject_partitions()
                                         for tpext_arr_by_tbl
                                         in triplets_by_table_arr]

        # triplets_tbl_util = TripletExtendedArrUtils(triplets_by_table_arr[0])
        # triplets_by_table_subject_arr = triplets_tbl_util.get_split_into_subject_partitions()

        sql0 = self.translate_one_table_one_subject_triplets_arr(triplets_by_table_subject_arr[0][0], Namer(), namer)
        sql1 = self.translate_one_table_triplets_arr_arr(triplets_by_table_subject_arr[0], namer)

        sql_partials_by_table = [self.translate_one_table_triplets_arr_arr(tp_ext_by_table_subject_arr, namer)
                                 for tp_ext_by_table_subject_arr
                                 in triplets_by_table_subject_arr]

        sql_combined = sql_partials_by_table[0]
        for sql in sql_partials_by_table:
            if sql == sql_combined:
                continue
            sql_combined = self.q1_and_q2(sql_combined, sql, Namer())

        return sql_combined

    def tps_arr_to_tps_ext_arr(self, triplets_arr: List[Triplet]) -> List[TripletExtended]:
        fabric = TripletExtendedFabric(self.rdf2rdb)
        triplets_ext_arr = fabric.convert_triplet_arr_to_extended_arr(triplets_arr)
        triplets_util = TripletExtendedArrUtils(triplets_ext_arr)
        triplets_util.sort()
        return triplets_ext_arr

    def apply_filter(self, partial_sql: QuerySQL, graph_sparql: Graph, var_namer: Namer) -> None:
        for condition in graph_sparql.filter.conditions_arr:
            if condition.is_function():
                raise NotImplementedError
            else:
                if not condition.is_complete():
                    raise Exception("Malformed condition found. Run with debuuger to inspect it")
                # something operator something
                left = str(partial_sql.select.rename_map_variable[var_namer.get_name(condition.operand_left)]) \
                    if self.checker.is_variable(condition.operand_left) \
                    else f'"{condition.operand_left}"'
                right = str(partial_sql.select.rename_map_variable[var_namer.get_name(condition.operand_right)]) \
                    if self.checker.is_variable(condition.operand_right) \
                    else f'"{condition.operand_right}"'
                if condition.operator_logical_previous == "" \
                        or condition.operator_logical_previous == SPARQLConst.opLogicalAnd:
                    partial_sql.where.and_condition_add(left, condition.operator, right)
                else:
                    raise NotImplementedError
        pass

    def translate_into_query_partial(self) -> QuerySQL:
        g_root = self.query.graph_temp
        g_traveler = GraphTraveler(g_root)
        graph = g_root
        tps_memory = TripletExtendedMemory()
        partial_q_previous = QuerySQL()
        partial_q_new = QuerySQL()
        tps_ext_arr_now = []
        level_previous = g_traveler.level_now
        while True:
            tps_ext_arr_now = self.tps_arr_to_tps_ext_arr(graph.triplets_arr)
            tps_memory.set_memory(g_traveler.level_now, tps_ext_arr_now)
            if graph != g_root:
                # operation something
                tps_memory.align_levels_to(g_traveler.level_now)
                if not TripletExtendedChecker.is_tps_ext_arr_resolved(tps_ext_arr_now, self.rdf2rdb):
                    tps_memory.level_max_allowed = g_traveler.level_now
                    tea_utils = TripletExtendedArrUtils(tps_ext_arr_now)
                    tea_utils.update_as_extension_of(tps_memory.get_allowed_memory(), self.rdf2rdb)

                partial_q_new = self.translate_graph_triplets_arr(tps_ext_arr_now)
                self.apply_filter(partial_q_new, graph, Namer())

                if graph.is_union:
                    partial_q_previous = self.q1_union_q2(partial_q_previous, partial_q_new, Namer())
                elif graph.is_optional:
                    partial_q_previous = self.q1_optional_q2(partial_q_previous, partial_q_new, Namer())
                else:
                    raise NotImplementedError
                level_previous = g_traveler.level_now
                pass
            else:
                # first step
                partial_q_new = self.translate_graph_triplets_arr(tps_ext_arr_now)
                self.apply_filter(partial_q_new, graph, Namer())
                partial_q_previous = partial_q_new

            graph = g_traveler.get_next_or_root()
            if graph == g_root:
                break
        return partial_q_previous

    def translate(self) -> str:
        result_q = self.translate_into_query_partial()
        projection_q = QuerySQL()
        projection_q.select.set_from_query_as_table(str(result_q), Namer().rename("result_q"))
        var_namer = Namer()
        projection_q.select.is_distinct = self.query.select.isDistinct
        for var in self.query.select.variables_arr:
            projection_q.select.variable_add(var_namer.get_name(var), "", "")
        for var in self.query.order.variables_arr:
            projection_q.order.variables_arr.append(projection_q.select.name_map_variable[var_namer.get_name(var)])
        projection_q.limit = self.query.limit
        projection_q.offset = self.query.offset
        return str(projection_q)
        pass
