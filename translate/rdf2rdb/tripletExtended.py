from SPARQL.triplet import Triplet
from translate.rdf2rdb.tripletExtendedType import TripletExtendedType


class TripletExtended(Triplet):
    def __init__(self, triplet: Triplet):
        super().__init__()
        self.is_root = False
        self.subject = triplet.subject
        self.predicate = triplet.predicate
        self.object = triplet.object
        self.table_subject = ""
        self.table_object = ""
        self.table_linking = ""
        self.type = TripletExtendedType.UNKNOWN

    # no need for datatype

    def is_linking(self):
        return self.table_linking != "" \
               and self.table_object != "" \
               and self.table_subject != ""

    def __str__(self):
        return f"{self.subject} {self.predicate} {self.object}"
