from SPARQL.query import Query
from structureMapUnpacked import StructureMapUnpacked
from translate.normaliserSPARQL import NormaliserSPARQL
from translate.rdf2rdb.tripletExtendedFabric import TripletExtendedFabric
from translate.rdf2rdb.translator import Translator as rdf2rdbTranslator


class Translator:
    def __init__(self, query: Query):
        self.query = query
        self.ontologyConverter = "rdf2rdb"  # no other supported

    def translate(self, structure_map: StructureMapUnpacked):
        if self.ontologyConverter == "rdf2rdb":
            return self.translate_for_rdf2rdb(structure_map)
        raise NotImplementedError(f"No support for {self.ontologyConverter} ontology converted found")

    def translate_for_rdf2rdb(self, rdf2rdb: StructureMapUnpacked) -> str:
        print("SPARQL query normalisation ...")
        normaliser = NormaliserSPARQL(self.query)
        normaliser.normalise_no_copy()
        print("SPARQL query normalisation ... Done")

        print("Performing SPARQL to SQL transformation for RDF2RDB schema ... ")
        translator = rdf2rdbTranslator(self.query, rdf2rdb)
        print("Performing SPARQL to SQL transformation for RDF2RDB schema ... Done")
        return translator.translate()
