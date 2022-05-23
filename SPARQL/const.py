class Const(object):
    prefix = "PREFIX"
    select = "SELECT"
    where = "WHERE"
    union = "UNION"
    bound = "BOUND"
    order = "ORDER"
    by = "BY"
    limit = "LIMIT"
    offset = "OFFSET"
    filter = "FILTER"
    distinct = "DISTINCT"
    optional = "OPTIONAL"

    prefixLeftMark = "<"
    prefixRightMark = ">"
    dataTypeMark = "^^"
    stringMarks_arr = ["'", '"']
    stringLongMarks_arr = ["'''", '"""']

    # -------------------------- operators
    opEqual = "="
    opLess = "<"
    opUnequal = "!="
    opLogicalAnd = "&&"

    operators_single_char = [opLess, opEqual]
    operators_double_char = [opUnequal]
    operators_double_char_first_char = [x[0] for x in operators_double_char]
    operators_logical_double_char = [opLogicalAnd]
    operators_logical_double_char_first_char = [x[0] for x in operators_logical_double_char]

    rdfType = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    rdfsSubClassOf = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
    xsdDefaultType = "^^http://www.w3.org/2001/XMLSchema#string"
