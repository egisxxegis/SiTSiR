import yaml

from SPARQL.parser import Parser, parser_from_filename
from SPARQL.queryFabric import QueryFabric
from SQL.join import Join
from SQL.joinType import JoinType
from settings import Settings
from structureMapUnpacked import StructureMapUnpacked
from translate.namer import Namer
from translate.normaliserSPARQL import NormaliserSPARQL
from translate.rdf2rdb.translator import Translator
from translate.rdf2rdb.tripletExtendedArrUtils import TripletExtendedArrUtils
from translate.rdf2rdb.tripletExtendedFabric import TripletExtendedFabric
from SPARQL.triplet import Triplet
from translate.translator import Translator as AbstractTranslator


def pretty_print_yes_no(title, boolean_result):
    print("Testing: " + title)
    outcome = "Success" if boolean_result else "----------------------------------- Failed"
    print(f'{outcome}\n---------------')
    return not boolean_result


if __name__ == '__main__':

    error = False

    if not error:
        the_answers_in = "selEct"
        the_answers_real = ["SELECT"]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("Uppercase construct", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = "\t\r\n SELECT\r\t\t\t\t\n"
        the_answers_real = ["SELECT"]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("Ignore insignificant symbols", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = "\t\r\n selEct\r\t\t\t\t\n    ?n"
        the_answers_real = ["SELECT", "?n"]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("Split parts", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = "      PREFIX p: <p/>PREFIX d:   <d#>"
        the_answers_real = ["PREFIX", "p:", "<p/>", "PREFIX", "d:", "<d#>"]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("Find prefix declaration", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = "?q.}FILTER(?q>=8)"
        the_answers_real = ["?q", ".", "}", "FILTER", "(", "?q", ">", "=", "8", ")"]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("Return seperately operators and stuff", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = "'''?q.}FILTER(?q >=8)'''^^xsd:string"
        the_answers_real = ["'''?q.}FILTER(?q >=8)'''", "^^xsd:string"]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("Long string literal1 and datatype", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = '"""?q.}FILTER(?q >=8)"""^^xsd:string'
        the_answers_real = ['"""?q.}FILTER(?q >=8)"""', "^^xsd:string"]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("Long string literal2 and datatype", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = '"?q.}FILTER(?q >=8)"^^xsd:string'
        the_answers_real = ['"?q.}FILTER(?q >=8)"', "^^xsd:string"]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("String literal1 and datatype", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = "'?q.}FILTER(?q >=8)'^^xsd:string"
        the_answers_real = ["'?q.}FILTER(?q >=8)'", "^^xsd:string"]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("String literal2 and datatype", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = "'?q.}FILTER(?q >=8)'^^xsd:string."
        the_answers_real = ["'?q.}FILTER(?q >=8)'", "^^xsd:string", "."]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("String literal2 and datatype", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = "8.08^^xsd:float."
        the_answers_real = ["8.08", "^^xsd:float", "."]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("Float datatype", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = "?var1&&?var2"
        the_answers_real = ["?var1", "&", "&", "?var2"]
        the_options = None
        the_answers_out = Parser(the_answers_in).get_all_parts()
        error = pretty_print_yes_no("Logical and", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query11.sparql"))
        the_answers_real = ["?ee"]
        the_options = None
        the_answers_out = the_answers_in.order.variables_arr
        error = pretty_print_yes_no("parse Query order by", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query11.sparql"))
        the_answers_real = [10, 50]
        the_options = None
        the_answers_out = [the_answers_in.limit, the_answers_in.offset]
        error = pretty_print_yes_no("parse Query limit and offset", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query02.sparql"))
        the_answers_real = [9, "?inproc", "rdfs:seeAlso", "?ee"]
        the_options = None
        the_answers_out = [len(the_answers_in.graph_temp.triplets_arr),
                           the_answers_in.graph_temp.triplets_arr[5].subject,
                           the_answers_in.graph_temp.triplets_arr[5].predicate,
                           the_answers_in.graph_temp.triplets_arr[5].object]
        error = pretty_print_yes_no("parse Query triplets. length + 6th triplet", the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query02.sparql"))
        the_answers_real = [1, "?inproc", "bench:abstract", "?abstract"]
        the_options = None
        the_answers_out = [len(the_answers_in.graph_temp.child.triplets_arr),
                           the_answers_in.graph_temp.child.triplets_arr[0].subject,
                           the_answers_in.graph_temp.child.triplets_arr[0].predicate,
                           the_answers_in.graph_temp.child.triplets_arr[0].object]
        error = pretty_print_yes_no("parse Query triplets. Optional length + 1st its triplet",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query02.sparql"))
        the_answers_real = [False, True]
        the_options = None
        the_answers_out = [the_answers_in.graph_temp.is_optional, the_answers_in.graph_temp.child.is_optional]
        error = pretty_print_yes_no("parse Query OPTIONAL. Is its type set correctly",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query09.sparql"))
        the_answers_real = [False, False, True]
        the_options = None
        the_answers_out = [the_answers_in.graph_temp.is_union, the_answers_in.graph_temp.child.is_union,
                           the_answers_in.graph_temp.child.next.is_union]
        error = pretty_print_yes_no("parse Query UNION. Is its type set correctly",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query09.sparql"))
        the_answers_real = [2, "?person", "rdf:type", "foaf:Person"]
        the_options = None
        the_answers_out = [len(the_answers_in.graph_temp.child.next.triplets_arr),
                           the_answers_in.graph_temp.child.next.triplets_arr[0].subject,
                           the_answers_in.graph_temp.child.next.triplets_arr[0].predicate,
                           the_answers_in.graph_temp.child.next.triplets_arr[0].object]
        error = pretty_print_yes_no("parse Query UNION. count of triplets inside and first triplet",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query08.sparql"))
        the_answers_real = [4, "?author", "!=", "?erdoes"]
        the_options = None
        the_answers_out = [len(the_answers_in.graph_temp.child.filter.conditions_arr),
                           the_answers_in.graph_temp.child.filter.conditions_arr[0].operand_left,
                           the_answers_in.graph_temp.child.filter.conditions_arr[0].operator,
                           the_answers_in.graph_temp.child.filter.conditions_arr[0].operand_right]
        error = pretty_print_yes_no("parse FILTER. count of conditions inside and first condition",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query08.sparql"))
        the_answers_real = [False, False, 0, "&&"]  # for "&&" check SPARQL.const.Const.opLogicalAnd
        the_options = None
        the_answers_out = [the_answers_in.graph_temp.child.filter.conditions_arr[3].is_function_negated,
                           the_answers_in.graph_temp.child.filter.conditions_arr[3].is_function(),
                           len(the_answers_in.graph_temp.child.filter.conditions_arr[3].arguments_arr),
                           the_answers_in.graph_temp.child.filter.conditions_arr[3].operator_logical_previous]
        error = pretty_print_yes_no("parse FILTER. no unnecessary flags set",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query06.sparql"))
        the_answers_real = [1,
                            "BOUND",
                            True,
                            1,
                            "?author2"]
        the_options = None
        the_answers_out = [len(the_answers_in.graph_temp.filter.conditions_arr),
                           the_answers_in.graph_temp.filter.conditions_arr[0].function,
                           the_answers_in.graph_temp.filter.conditions_arr[0].is_function_negated,
                           len(the_answers_in.graph_temp.filter.conditions_arr[0].arguments_arr),
                           the_answers_in.graph_temp.filter.conditions_arr[0].arguments_arr[0]]
        error = pretty_print_yes_no("parse FILTER. negated BOUND",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = ["query01.sparql", "query02.sparql", "query03a.sparql",
                          "query03b.sparql", "query03c.sparql", "query04.sparql",
                          "query05a.sparql", "query05b.sparql", "query06.sparql",
                          "query07.sparql", "query08.sparql", "query09.sparql",
                          "query10.sparql", "query11.sparql"]
        the_answers_real = [True] * len(the_answers_in)
        the_options = None
        the_answers_out = [QueryFabric().query_from_parser(parser_from_filename('test_data\\' + queryFile)) is not None
                           for queryFile in the_answers_in]
        error = pretty_print_yes_no("parse all sp2b queries", the_answers_real == the_answers_out)

# ----------------------------------
# ----- DATA DEPENDANT!!!
# ----------------------------------

    if not error:
        the_answers_in = ["name", "http://xmlns.com/foaf/0.1/name", "ze#person#name", "qq#name/person"]
        with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
            rdf2rdb: StructureMapUnpacked = yaml.unsafe_load(mapFile)
        the_options = []
        the_answers_real = ["name", "name", "name", "person"]
        the_answers_out = [rdf2rdb.get_property_unsafe(prop) for prop in the_answers_in]
        error = pretty_print_yes_no("Unsafe property extraction",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = [Triplet(), Triplet()]
        the_answers_in[0].set_subject("?inproc")
        the_answers_in[0].set_predicate("http://purl.org/dc/elements/1.1/creator")
        the_answers_in[0].set_object("?author")
        the_answers_in[1].set_subject("?inproc")
        the_answers_in[1].set_predicate("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        the_answers_in[1].set_object("http://localhost/vocabulary/bench/Inproceedings")
        with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
            rdf2rdb = yaml.unsafe_load(mapFile)
        the_options = TripletExtendedFabric(rdf2rdb)
        the_answers_in = the_options.convert_triplet_arr_to_extended_arr(the_answers_in)
        the_answers_real = [False, True]
        the_answers_out = [the_answers_in[0].is_root, the_answers_in[1].is_root]
        error = pretty_print_yes_no("TripletExtended. Are root entries found?",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = [Triplet(), Triplet(), Triplet()]
        the_answers_in[0].set_subject("?inproc")
        the_answers_in[0].set_predicate("http://purl.org/dc/elements/1.1/creator")
        the_answers_in[0].set_object("?author")
        the_answers_in[1].set_subject("?inproc")
        the_answers_in[1].set_predicate("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        the_answers_in[1].set_object("http://localhost/vocabulary/bench/Inproceedings")
        the_answers_in[2].set_subject("?dunno")
        the_answers_in[2].set_predicate("zeWhat")
        the_answers_in[2].set_object("object")
        with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
            rdf2rdb = yaml.unsafe_load(mapFile)
        the_options = TripletExtendedFabric(rdf2rdb)
        the_answers_in = the_options.convert_triplet_arr_to_extended_arr(the_answers_in)
        the_answers_real = ["inproceedings",
                            "inproceedings",
                            ""]
        the_answers_out = [the_answers_in[0].table_subject,
                           the_answers_in[1].table_subject,
                           the_answers_in[2].table_subject]
        error = pretty_print_yes_no("TripletExtended. Is table subject assigned correctly?",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = [Triplet(), Triplet()]
        the_answers_in[0].set_subject("?inproc")
        the_answers_in[0].set_predicate("http://purl.org/dc/elements/1.1/creator")
        the_answers_in[0].set_object("?author")
        the_answers_in[1].set_subject("?inproc")
        the_answers_in[1].set_predicate("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        the_answers_in[1].set_object("http://localhost/vocabulary/bench/Inproceedings")
        with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
            rdf2rdb = yaml.unsafe_load(mapFile)
        the_options = TripletExtendedFabric(rdf2rdb)
        the_answers_in = the_options.convert_triplet_arr_to_extended_arr(the_answers_in)
        the_answers_real = [True,
                            "inproceedings_creator_person",
                            "person"]
        the_answers_out = [the_answers_in[0].is_linking(),
                           the_answers_in[0].table_linking,
                           the_answers_in[0].table_object]
        error = pretty_print_yes_no("sort TripletExtended. half chain Linking entry found",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = [Triplet(), Triplet(), Triplet()]
        the_answers_in[0].set_subject("?inproc")
        the_answers_in[0].set_predicate("http://purl.org/dc/elements/1.1/creator")
        the_answers_in[0].set_object("?author")
        the_answers_in[1].set_subject("?inproc")
        the_answers_in[1].set_predicate("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        the_answers_in[1].set_object("http://localhost/vocabulary/bench/Inproceedings")
        the_answers_in[2].set_subject("?author")
        the_answers_in[2].set_predicate("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        the_answers_in[2].set_object("http://xmlns.com/foaf/0.1/Person")
        with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
            rdf2rdb = yaml.unsafe_load(mapFile)
        the_options = TripletExtendedFabric(rdf2rdb)
        the_answers_in = the_options.convert_triplet_arr_to_extended_arr(the_answers_in)
        the_answers_real = [True,
                            "inproceedings_creator_person",
                            "person",
                            "person"]
        the_answers_out = [the_answers_in[0].is_linking(),
                           the_answers_in[0].table_linking,
                           the_answers_in[0].table_object,
                           the_answers_in[2].table_subject]
        error = pretty_print_yes_no("sort TripletExtended. full chain Linking entry found",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = [Triplet(), Triplet(), Triplet()]
        the_answers_in[0].set_subject("?inproc")
        the_answers_in[0].set_predicate("http://purl.org/dc/elements/1.1/creator")
        the_answers_in[0].set_object("?author")
        the_answers_in[1].set_subject("?inproc")
        the_answers_in[1].set_predicate("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        the_answers_in[1].set_object("http://localhost/vocabulary/bench/Inproceedings")
        the_answers_in[2].set_subject("?author")
        the_answers_in[2].set_predicate("name")
        the_answers_in[2].set_object("?dunno")
        with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
            rdf2rdb = yaml.unsafe_load(mapFile)
        the_options = TripletExtendedFabric(rdf2rdb)
        the_answers_in = the_options.convert_triplet_arr_to_extended_arr(the_answers_in)
        the_answers_real = [True,
                            "inproceedings_creator_person",
                            "person",
                            "person"]
        the_answers_out = [the_answers_in[0].is_linking(),
                           the_answers_in[0].table_linking,
                           the_answers_in[0].table_object,
                           the_answers_in[2].table_subject]
        error = pretty_print_yes_no("sort TripletExtended. full chain Linking entry found and helped to fill info",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = [Triplet(), Triplet()]
        the_answers_in[0].set_subject("?inproc")
        the_answers_in[0].set_predicate("http://purl.org/dc/elements/1.1/creator")
        the_answers_in[0].set_object("?author")
        the_answers_in[1].set_subject("?inproc")
        the_answers_in[1].set_predicate("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        the_answers_in[1].set_object("http://localhost/vocabulary/bench/Inproceedings")
        with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
            rdf2rdb = yaml.unsafe_load(mapFile)
        the_options = TripletExtendedFabric(rdf2rdb)
        the_answers_in = the_options.convert_triplet_arr_to_extended_arr(the_answers_in)
        the_options = TripletExtendedArrUtils(the_answers_in)
        the_options.sort()
        the_answers_real = "?author"
        the_answers_out = the_answers_in[1].object
        error = pretty_print_yes_no("sort TripletExtended. Linking entries must be after normal entries",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = Join("root", "branch")
        the_options = []
        the_answers_in.type = JoinType.INNER
        the_answers_in.table_to_be_joined_rename = "branch_rename"
        the_answers_in.set_columns("root_id", "root_id1")
        the_answers_real = "INNER JOIN branch AS branch_rename " \
                           "\nON 1 " \
                           "\nAND root.root_id = branch_rename.root_id1"
        the_answers_out = the_answers_in.__str__()
        error = pretty_print_yes_no("full Join object to string",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = Join("root", "branch")
        the_options = []
        the_answers_in.type = JoinType.LEFT
        the_answers_in.table_to_be_joined_rename = "branch_rename"
        the_answers_real = "LEFT OUTER JOIN branch AS branch_rename " \
                           "\nON 1"
        the_answers_out = the_answers_in.__str__()
        error = pretty_print_yes_no("partial Join object to string",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = Join("root", "branch")
        the_options = []
        the_answers_in.type = JoinType.LEFT
        the_answers_real = "LEFT OUTER JOIN branch " \
                           "\nON 1"
        the_answers_out = the_answers_in.__str__()
        error = pretty_print_yes_no("minimum Join object to string",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query01.sparql"))
        # -------- METHOD DUMP. partial translation of the simplest query.
        normaliser = NormaliserSPARQL(the_answers_in)
        normaliser.normalise_no_copy()
        with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
            rdf2rdb = yaml.unsafe_load(mapFile)
        fabric = TripletExtendedFabric(rdf2rdb)
        triplets_ext_arr = fabric.convert_triplet_arr_to_extended_arr(the_answers_in.graph_temp.triplets_arr)
        triplets_util = TripletExtendedArrUtils(triplets_ext_arr)
        namer = Namer()

        triplets_util.sort()
        translator = Translator(the_answers_in, rdf2rdb)
        variables_arr = translator.extract_variables_all(triplets_ext_arr)
        triplets_by_table_arr = translator.triplets_ext_arr_to_triplets_ext_arr_arr(triplets_ext_arr)

        triplets_tbl_util = TripletExtendedArrUtils(triplets_by_table_arr[0])
        triplets_by_table_subject_arr = triplets_tbl_util.get_split_into_subject_partitions()

        sql0 = translator.translate_one_table_one_subject_triplets_arr(triplets_by_table_subject_arr[0], Namer(), namer)
        # -------- METHOD DUMP END
        the_answers_real = "SELECT %%table%%.uri as \"journal\", \n%%table%%.issued as \"yr\" " \
                           "\nFROM journal AS %%table%% \nWHERE %%table%%.title = \"Journal 1 (1940)\" " \
                           "\nAND %%table%%.issued IS NOT NULL"
        the_answers_real = the_answers_real.replace("%%table%%", sql0.select.table_renames_arr[0])
        the_answers_out = sql0.select.__str__() + " \n" + sql0.where.__str__()
        error = pretty_print_yes_no("Translate partial query01 to SQL",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query02.sparql"))
        # -------- METHOD DUMP. partial translation of the second query.
        normaliser = NormaliserSPARQL(the_answers_in)
        normaliser.normalise_no_copy()
        with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
            rdf2rdb = yaml.unsafe_load(mapFile)
        fabric = TripletExtendedFabric(rdf2rdb)
        translator = Translator(the_answers_in, rdf2rdb)

        sql0 = translator.translate_into_query_partial()
        # -------- METHOD DUMP END
        the_answers_real = "SELECT DISTINCT %%q1%%.yr, \n%%q1%%.booktitle, \n%%q1%%.title, \n%%q1%%.url, " \
                           "\n%%q1%%.ee, \n%%q1%%.page, \n%%q1%%.proc, \n%%q1%%.author, " \
                           "\n%%q2%%.abstract, \nCOALESCE(%%q1%%.inproc, %%q2%%.inproc) as \"inproc\" " \
                           "\nFROM (SELECT %%t1%%.uri as \"inproc\", \n%%t1%%.issued as \"yr\", " \
                           "\n%%t1%%.booktitle as \"booktitle\", \n%%t1%%.title as \"title\", " \
                           "\n%%t1%%.homepage as \"url\", \n%%t1%%.seealso as \"ee\", \n%%t1%%.pages as \"page\", " \
                           "\n%%t2%%.uri as \"proc\", \n%%t4%%.uri as \"author\" \nFROM inproceedings AS %%t1%%" \
                           "\nINNER JOIN inproceedings_partof_proceedings AS %%t3%% \nON 1 " \
                           "\nAND %%t1%%.inproceedings_id = %%t3%%.inproceedings_id1" \
                           "\nINNER JOIN proceedings AS %%t2%% \nON 1 " \
                           "\nAND %%t3%%.proceedings_id2 = %%t2%%.proceedings_id" \
                           "\nINNER JOIN inproceedings_creator_person AS %%t5%% \nON 1 " \
                           "\nAND %%t1%%.inproceedings_id = %%t5%%.inproceedings_id1\nINNER JOIN person AS %%t4%% " \
                           "\nON 1 \nAND %%t5%%.person_id2 = %%t4%%.person_id\nWHERE %%t1%%.issued IS NOT NULL " \
                           "\nAND %%t1%%.booktitle IS NOT NULL \nAND %%t1%%.title IS NOT NULL " \
                           "\nAND %%t1%%.homepage IS NOT NULL \nAND %%t1%%.seealso IS NOT NULL " \
                           "\nAND %%t1%%.pages IS NOT NULL) AS %%q1%%" \
                           "\nLEFT OUTER JOIN (SELECT %%t6%%.uri as \"inproc\", \n%%t6%%.abstract as \"abstract\" " \
                           "\nFROM inproceedings AS %%t6%%\nWHERE %%t6%%.abstract IS NOT NULL) AS %%q2%% " \
                           "\nON 1 \nAND 1 \nAND ( %%q1%%.inproc = %%q2%%.inproc \nOR %%q1%%.inproc IS NULL " \
                           "\nOR %%q2%%.inproc IS NULL )" \
                           "\nWHERE 1"
        the_answers_out = str(sql0)
        q1_name = the_answers_out.split("COALESCE(", 1)[1].split(".", 1)[0]
        q2_name = the_answers_out.split("COALESCE(", 1)[1].split(".", 2)[1].split(", ", 1)[1]
        t1_name = the_answers_out.split("FROM (SELECT ")[1].split(".", 1)[0]
        t2_name = the_answers_out.split(".uri as \"proc\",", 1)[0].split("page\", \n", 1)[1]
        t3_name = the_answers_out.split("inproceedings_partof_proceedings AS ", 1)[1].split(" ", 1)[0]
        t4_name = the_answers_out.split(" person AS ", 1)[1].split(" ", 1)[0]
        t5_name = the_answers_out.split("_person AS ", 1)[1].split(" ", 1)[0]
        t6_name = the_answers_out.split("JOIN (SELECT ", 1)[1].split(".", 1)[0]
        the_answers_real = the_answers_real.replace("%%q1%%", q1_name)
        the_answers_real = the_answers_real.replace("%%q2%%", q2_name)
        the_answers_real = the_answers_real.replace("%%t1%%", t1_name)
        the_answers_real = the_answers_real.replace("%%t2%%", t2_name)
        the_answers_real = the_answers_real.replace("%%t3%%", t3_name)
        the_answers_real = the_answers_real.replace("%%t4%%", t4_name)
        the_answers_real = the_answers_real.replace("%%t5%%", t5_name)
        the_answers_real = the_answers_real.replace("%%t6%%", t6_name)
        error = pretty_print_yes_no("Translate partial query02 to SQL",
                                    the_answers_real == the_answers_out)

    if not error:
        the_answers_in = QueryFabric().query_from_parser(parser_from_filename(r"test_data\query02.sparql"))
        # -------- METHOD DUMP. partial translation of the second query.
        with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
            rdf2rdb = yaml.unsafe_load(mapFile)
        translator = AbstractTranslator(the_answers_in)
        sql = translator.translate(rdf2rdb)
        # -------- METHOD DUMP END
        the_answers_real = "SELECT inproc, \nauthor, \nbooktitle, \ntitle, \nproc, \nee, \npage, \nurl, \nyr, " \
                           "\nabstract " \
                           "\nFROM (SELECT DISTINCT %%q1%%.yr, \n%%q1%%.booktitle, \n%%q1%%.title, \n%%q1%%.url, " \
                           "\n%%q1%%.ee, \n%%q1%%.page, \n%%q1%%.proc, \n%%q1%%.author, " \
                           "\n%%q2%%.abstract, \nCOALESCE(%%q1%%.inproc, %%q2%%.inproc) as \"inproc\" " \
                           "\nFROM (SELECT %%t1%%.uri as \"inproc\", \n%%t1%%.issued as \"yr\", " \
                           "\n%%t1%%.booktitle as \"booktitle\", \n%%t1%%.title as \"title\", " \
                           "\n%%t1%%.homepage as \"url\", \n%%t1%%.seealso as \"ee\", \n%%t1%%.pages as \"page\", " \
                           "\n%%t2%%.uri as \"proc\", \n%%t4%%.uri as \"author\" \nFROM inproceedings AS %%t1%%" \
                           "\nINNER JOIN inproceedings_partof_proceedings AS %%t3%% \nON 1 " \
                           "\nAND %%t1%%.inproceedings_id = %%t3%%.inproceedings_id1" \
                           "\nINNER JOIN proceedings AS %%t2%% \nON 1 " \
                           "\nAND %%t3%%.proceedings_id2 = %%t2%%.proceedings_id" \
                           "\nINNER JOIN inproceedings_creator_person AS %%t5%% \nON 1 " \
                           "\nAND %%t1%%.inproceedings_id = %%t5%%.inproceedings_id1\nINNER JOIN person AS %%t4%% " \
                           "\nON 1 \nAND %%t5%%.person_id2 = %%t4%%.person_id\nWHERE %%t1%%.issued IS NOT NULL " \
                           "\nAND %%t1%%.booktitle IS NOT NULL \nAND %%t1%%.title IS NOT NULL " \
                           "\nAND %%t1%%.homepage IS NOT NULL \nAND %%t1%%.seealso IS NOT NULL " \
                           "\nAND %%t1%%.pages IS NOT NULL) AS %%q1%%" \
                           "\nLEFT OUTER JOIN (SELECT %%t6%%.uri as \"inproc\", \n%%t6%%.abstract as \"abstract\" " \
                           "\nFROM inproceedings AS %%t6%%\nWHERE %%t6%%.abstract IS NOT NULL) AS %%q2%% " \
                           "\nON 1 \nAND 1 \nAND ( %%q1%%.inproc = %%q2%%.inproc \nOR %%q1%%.inproc IS NULL " \
                           "\nOR %%q2%%.inproc IS NULL )" \
                           "\nWHERE 1) AS %%p1%%\nWHERE 1 \nORDER BY yr"
        the_answers_out = str(sql)
        q1_name = the_answers_out.split("COALESCE(", 1)[1].split(".", 1)[0]
        q2_name = the_answers_out.split("COALESCE(", 1)[1].split(".", 2)[1].split(", ", 1)[1]
        t1_name = the_answers_out.split("FROM (SELECT ")[2].split(".", 1)[0]
        t2_name = the_answers_out.split(".uri as \"proc\",", 1)[0].split("page\", \n", 1)[1]
        t3_name = the_answers_out.split("inproceedings_partof_proceedings AS ", 1)[1].split(" ", 1)[0]
        t4_name = the_answers_out.split(" person AS ", 1)[1].split(" ", 1)[0]
        t5_name = the_answers_out.split("_person AS ", 1)[1].split(" ", 1)[0]
        t6_name = the_answers_out.split("JOIN (SELECT ", 1)[1].split(".", 1)[0]
        p1_name = the_answers_out.split("\nWHERE 1 \nORDER BY yr")[0].split(" ")[-1]
        the_answers_real = the_answers_real.replace("%%q1%%", q1_name)
        the_answers_real = the_answers_real.replace("%%q2%%", q2_name)
        the_answers_real = the_answers_real.replace("%%t1%%", t1_name)
        the_answers_real = the_answers_real.replace("%%t2%%", t2_name)
        the_answers_real = the_answers_real.replace("%%t3%%", t3_name)
        the_answers_real = the_answers_real.replace("%%t4%%", t4_name)
        the_answers_real = the_answers_real.replace("%%t5%%", t5_name)
        the_answers_real = the_answers_real.replace("%%t6%%", t6_name)
        the_answers_real = the_answers_real.replace("%%p1%%", p1_name)
        error = pretty_print_yes_no("Translate full query02 to SQL",
                                    the_answers_real == the_answers_out)

    if error:
        print("Expected: ")
        print(the_answers_real)
        print("Got: ")
        print(the_answers_out)
