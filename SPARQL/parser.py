from SPARQL.const import Const


class Parser:
    def __init__(self, query: str):
        self.query = query
        self.position = 0

        self.last_returned_part = ""
        self.last_second_returned_part = ""

        self.queryLen = len(query)
        self.terminators_arr = [" ", "\t", "\r", "\n"]
        self.constructs_arr = [Const.select, Const.prefix, Const.where, Const.order, Const.by, Const.limit,
                               Const.offset, Const.filter, Const.distinct, Const.union, Const.bound, Const.optional]
        self.stringMarks_arr = [*Const.stringMarks_arr]
        self.stringLongMarks_arr = [*Const.stringLongMarks_arr]
        self.prefixLeftMark = Const.prefixLeftMark
        self.prefixRightMark = Const.prefixRightMark
        self.dataTypeMark = Const.dataTypeMark
        self.returnSeparately_arr = [".", "(", ")", "{", "}", "<", ">", "=", "!", "&", ",", "|"]

    @staticmethod
    def is_string_literal_wrapped(part: str, string_mark: str) -> bool:
        if len(part) < len(string_mark) * 2:
            return False
        return part.endswith(string_mark) and part.startswith(string_mark)

    def is_string_literal_mark_to_be_longer(self, mark: str, next_read_pos: int) -> bool:
        if next_read_pos >= len(self.query):
            return False
        new_part = mark + self.query[next_read_pos]
        return new_part in self.stringLongMarks_arr

    def get_next_part(self):
        i = self.position
        part = ""
        started = False
        is_string_literal = False
        is_prefix = False

        string_literal_mark = ""
        for i in range(i, self.queryLen):
            # terminator found
            if self.query[i] in self.terminators_arr:
                if is_string_literal:
                    if self.is_string_literal_wrapped(part, string_literal_mark):
                        break
                    else:
                        part += self.query[i]
                        continue
                elif started:
                    break
                else:
                    continue

            # part starts
            started = True
            part += self.query[i]

            # is it string literal
            if len(part) == 1 and part[0] in self.stringMarks_arr:
                is_string_literal = True
                string_literal_mark = part[0]
                continue

            if len(part) == 3 and part[0:3] in self.stringLongMarks_arr:
                is_string_literal = True
                string_literal_mark = part[0:3]
                continue

            if is_string_literal and self.is_string_literal_wrapped(part, string_literal_mark)\
                    and not self.is_string_literal_mark_to_be_longer(part, i + 1):
                break

            # is it prefix wrapper
            if len(part) == 1 and part[0] == self.prefixLeftMark:
                if self.last_second_returned_part == "PREFIX":
                    is_prefix = True
                    continue

            if is_prefix and part[-1] == self.prefixRightMark:
                break

            if not is_prefix and not is_string_literal:
                # is it datatype
                if len(part) > 2 and part[-2:] == self.dataTypeMark:
                    part = part[0:-2]
                    i -= 2
                    break

                # is it return separately
                if part[-1] in self.returnSeparately_arr:
                    # let floats 8.08 live
                    if part[-1] == '.' and part[:-1].isnumeric():
                        continue
                    if len(part) > 1:
                        i -= 1
                        part = part[0:-1]
                    break
        # end of for loop

        # parse part
        self.position = i + 1
        part = part.upper() if (part.upper() in self.constructs_arr) else part
        self.last_second_returned_part = self.last_returned_part
        self.last_returned_part = part
        return part

    def get_all_parts(self) -> [str]:
        parts = []
        while self.get_next_part() != "":
            parts.append(self.last_returned_part)
        return parts

    def reset(self) -> None:
        self.position = 0
        self.last_returned_part = ""
        self.last_second_returned_part = ""


def parser_from_filename(filename: str) -> Parser:
    with open(filename, 'r') as queryInputFile:
        return Parser(queryInputFile.read())
