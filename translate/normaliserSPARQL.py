from SPARQL.query import Query
from SPARQL.triplet import Triplet
from SPARQL.const import Const
from SPARQL.graph import Graph
from SPARQL.conditon import Condition
from translate.graphTraveler import GraphTraveler


class NormaliserSPARQL:
    def __init__(self, query: Query):
        self.query = query
        self.graphRoot = query.graph_temp
        pass

    def prefixed_string_unpack(self, string: str) -> str:
        # abc:qqq         -> the_abc_url#qqq
        # the_abc_url#qqq -> the_abc_url#qqq
        names_arr = self.query.name_map_prefix.keys()
        names_len_arr = [len(name) for name in names_arr]
        name_len_min = min(names_len_arr)
        name_len_max = max(names_len_arr)
        for length in range(name_len_min, name_len_max + 1):
            if len(string) < length:
                return string
            name = string[0:length]
            if name in names_arr:
                return self.query.get_prefix_from_name_map(name).translate(string)
        return string

    def prefixed_datatype_unpack(self, datatype: str) -> str:
        # ^^xsd:qqq    -> ^^the_xsd_url:qqq
        # ^^notUri:qqq -> ^^notUri:qqq
        return "^^" + self.prefixed_string_unpack(datatype[2:])

    def triplet_prefix_unpack(self, triplet: Triplet) -> None:
        triplet.set_subject(
            self.prefixed_string_unpack(triplet.subject),
            self.prefixed_datatype_unpack(triplet.subjectDataType)
        )

        if triplet.predicate == "a":
            triplet.set_predicate(
                Const.rdfType,
                self.prefixed_datatype_unpack(triplet.subjectDataType)
            )
        else:
            triplet.set_predicate(
                self.prefixed_string_unpack(triplet.predicate),
                self.prefixed_datatype_unpack(triplet.predicateDataType)
            )

        triplet.set_object(
            self.prefixed_string_unpack(triplet.object),
            self.prefixed_datatype_unpack(triplet.objectDataType)
        )
        return

    def condition_prefix_unpack(self, condition: Condition) -> None:
        if condition.is_function():
            return
        condition.operand_left = self.prefixed_string_unpack(condition.operand_left)
        condition.operand_right = self.prefixed_string_unpack(condition.operand_right)
        # no case of function(URL) in sp2b

    def triplets_unpack(self) -> None:
        graph = self.graphRoot
        graph_traveler = GraphTraveler(graph)
        while True:
            for triplet in graph.triplets_arr:
                self.triplet_prefix_unpack(triplet)
            graph = graph_traveler.get_next_or_root()
            if graph == self.graphRoot:
                break

    def filters_unpack(self) -> None:
        graph = self.graphRoot
        graph_traveler = GraphTraveler(graph)
        while True:
            for condition in graph.filter.conditions_arr:
                self.condition_prefix_unpack(condition)
            graph = graph_traveler.get_next_or_root()
            if graph == self.graphRoot:
                break

    def normalise_no_copy(self) -> None:
        self.triplets_unpack()
        self.filters_unpack()
