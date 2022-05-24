from SPARQL.const import Const


class Triplet:
    dataTypeDefault = Const.xsdDefaultType

    def __init__(self):
        self.subject = ""
        self.subjectDataType = ""
        self.predicate = ""
        self.predicateDataType = ""
        self.object = ""
        self.objectDataType = ""

    def set_subject(self, subject: str, datatype_raw=None):
        datatype_raw = self.dataTypeDefault if datatype_raw is None else datatype_raw
        self.subject = subject
        self.subjectDataType = datatype_raw

    def set_predicate(self, predicate: str, datatype_raw=None):
        datatype_raw = self.dataTypeDefault if datatype_raw is None else datatype_raw
        self.predicate = predicate
        self.predicateDataType = datatype_raw

    def set_object(self, the_object: str, datatype_raw=None):
        datatype_raw = self.dataTypeDefault if datatype_raw is None else datatype_raw
        self.object = the_object
        self.objectDataType = datatype_raw

    def __str__(self):
        return f"{self.subject} {self.predicate} {self.object}"
