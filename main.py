import yaml
from settings import Settings
from structureMapUnpacked import StructureMapUnpacked  # must for yaml load, DO NOT DELETE
from SPARQL.parser import Parser
from SPARQL.queryFabric import QueryFabric
from translate.translator import Translator

if __name__ == '__main__':
    with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
        rdf2rdb = yaml.unsafe_load(mapFile)
    with open(Settings.queryInputFile, 'r') as queryInputFile:
        queryRaw = queryInputFile.read()
    parser = Parser(queryRaw)
    parts = parser.get_all_parts()
    parser.reset()

    # for part in parts:
    #     print(part)

    queryFabric = QueryFabric()
    query = queryFabric.query_from_parser(parser)

    translator = Translator(query)
    sql_as_string = translator.translate(rdf2rdb)
    with open(Settings.queryOutputFile, "w") as outputFile:
        outputFile.write(sql_as_string)
    print(sql_as_string[0:300])
    print("...")
    print("\n\n")
    print(f"Transformation complete. Check file {Settings.queryOutputFile} for full query")
