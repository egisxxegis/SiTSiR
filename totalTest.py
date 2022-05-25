import yaml

from SPARQL.parser import Parser
from SPARQL.queryFabric import QueryFabric
from settings import Settings
from translate.translator import Translator

with open(Settings.rdf2rdbMapFile, 'r') as mapFile:
    rdf2rdb = yaml.unsafe_load(mapFile)

inputs = [f"test_data/query0{x}.sparql" for x in [1, 2, "3a", "3b", 4, "5a", "5b"]]
for sparqlIn in inputs:
    print(f"Translating {sparqlIn}")
    with open(sparqlIn, 'r') as queryInputFile:
        queryRaw = queryInputFile.read()
    parser = Parser(queryRaw)
    queryFabric = QueryFabric()
    query = queryFabric.query_from_parser(parser)
    translator = Translator(query)
    sql_as_string = translator.translate(rdf2rdb)

illegal_inputs = [f"test_data/query{x}.sparql" for x in ["06", "07", "08", "09", "10", "11"]]
loglog = []
for sparqlIn in illegal_inputs:
    print(f"Translating {sparqlIn}")
    loglog.append(f"Translating {sparqlIn}")
    with open(sparqlIn, 'r') as queryInputFile:
        queryRaw = queryInputFile.read()
    parser = Parser(queryRaw)
    queryFabric = QueryFabric()
    query = queryFabric.query_from_parser(parser)
    translator = Translator(query)
    try:
        sql_as_string = translator.translate(rdf2rdb)
    except Exception:
        print(f"Translating {sparqlIn} FAILED")
        loglog.append(f"Translating {sparqlIn} FAILED")

print("-----------------")
for log in loglog:
    print(log)


loglog.clear()
inputs.extend(illegal_inputs)
for sparqlIn in inputs:
    with open(sparqlIn, 'r') as queryInputFile:
        queryRaw = queryInputFile.read()
    parser = Parser(queryRaw)
    queryFabric = QueryFabric()
    query = queryFabric.query_from_parser(parser)
    translator = Translator(query)
    try:
        sql_as_string = translator.translate(rdf2rdb)
        loglog.append(f"Translating {sparqlIn} SUCCESS")
    except Exception:
        loglog.append(f"Translating {sparqlIn} -------- FAILED")

print("------------------------------------------")
print("------------------------------------------")
print("------------------------------------------")
for log in loglog:
    print(log)
