from SPARQL.parser import Parser
from SPARQL.queryFabricState import QueryFabricState as State
from SPARQL.const import Const
from SPARQL.query import Query


class QueryFabric:
    def __init__(self):
        self.state = State.ERROR
        self.state_history_arr: [State] = []

    def query_from_parser(self, parser: Parser) -> Query:
        parts_arr = []
        # part = ""
        self.state = State.INIT
        self.state_history_arr = [self.state]
        preserved_states_arr = [self.state]
        preserved_parts_arr_arr = [parts_arr]
        query = Query()

        def is_part_empty(the_part: str) -> bool:
            return the_part == ""

        def get_next_part() -> str:
            the_part = parser.get_next_part()
            if not is_part_empty(the_part):
                parts_arr.append(the_part)
            return the_part

        def predict_state_after_where(new_part: str) -> State:
            if new_part == Const.order:
                return State.ORDER_BY
            elif new_part == Const.limit:
                return State.LIMIT
            elif new_part == Const.offset:
                return State.OFFSET
            return self.state

        def predict_state_inner_start(new_part: str) -> State:
            # inside WHERE, inside OPTIONAL
            if new_part == Const.optional:
                return State.OPTIONAL
            if new_part == Const.filter:
                return State.FILTER
            if new_part == Const.union:
                return State.UNION
            # there are no cases when first thing is url or blank node
            # there are no cases when variable name starts with $
            if new_part.startswith("?") or new_part.startswith("$"):
                return State.SUBJECT
            if new_part == "}":
                # WHERE { }
                if self.state == State.WHERE:
                    return State.WHERE_END
                if self.state == State.OPTIONAL:
                    return State.OPTIONAL_END
                if len(preserved_states_arr) > 1:
                    if preserved_states_arr[-2] == State.WHERE:
                        return State.WHERE_END
                    if preserved_states_arr[-2] == State.OPTIONAL:
                        return State.OPTIONAL_END
                    if preserved_states_arr[-2] == State.UNION:
                        return State.UNION_END
                    if preserved_states_arr[-2] == State.GRAPH_START:
                        return State.GRAPH_END
                return State.GRAPH_END

            # make this "if" the very last
            elif new_part == "{":
                return State.GRAPH_START
            return State.ERROR

        def predict_state_inner_filter(new_part: str, is_allow_unsafe=False):
            if self.state in [State.FILTER,
                              State.LOGICAL_OR,
                              State.LOGICAL_AND]:
                # is it negation, variable, function
                # ! bound (
                if new_part == "!":
                    return State.NEGATION
                # bound (
                if new_part == Const.bound:
                    return State.BOUND
                # URL or variable
                return State.LEFT_OPERAND
            elif self.state == State.NEGATION:
                if new_part == Const.bound:
                    return State.BOUND
                # no case of ! ?var1 in sp2b
            elif self.state == State.LEFT_OPERAND:
                # ?var >
                if len(parts_arr) == 2:
                    if parts_arr[-1] in Const.operators_single_char \
                            or parts_arr[-1] in Const.operators_double_char_first_char:
                        return State.OPERATOR
            elif self.state == State.OPERATOR:
                if len(parts_arr) == 2:
                    if parts_arr[-2] + parts_arr[-1] in Const.operators_double_char:
                        return State.OPERATOR
                # no such case was found in sp2b
                # if parts_arr == "!":
                #     return State.NEGATION
                if parts_arr[-1] != ")":
                    return State.RIGHT_OPERAND
            elif self.state == State.RIGHT_OPERAND:
                # ?var2 )
                if new_part == ")":
                    return State.FILTER_END
                # sp2b has no case of "! ?var2 )"
                # ?var2 &
                elif len(parts_arr) == 2:
                    if new_part in Const.operators_logical_double_char_first_char:
                        return State.LOGICAL_UNKNOWN
                #  & &
            elif self.state == State.LOGICAL_UNKNOWN:
                if len(parts_arr) == 2:
                    parts_combined = parts_arr[-2] + new_part
                    if parts_combined in Const.operators_logical_double_char:
                        if parts_combined == Const.opLogicalAnd:
                            return State.LOGICAL_AND
                        # no case of OR in sp2b

            if is_allow_unsafe:
                if new_part == ")":
                    return State.FILTER_END

                elif new_part == "!":
                    return State.NEGATION
                return State.LEFT_OPERAND

            return State.ERROR

        def predict_state() -> State:
            new_part = parts_arr[-1]
            if self.state == State.INIT:
                # first keyword will be the input
                if len(parts_arr) > 1:
                    raise Exception("Unexpected start of query with keyword: " + new_part)
                if new_part == Const.prefix:
                    return State.PREFIX
                if new_part == Const.select:
                    return State.SELECT

            elif self.state == State.PREFIX:
                if new_part == Const.select:
                    return State.SELECT
                return State.PREFIX

            elif self.state == State.SELECT:
                if new_part == Const.where:
                    return State.WHERE
                return State.SELECT

            elif self.state == State.WHERE:
                if len(parts_arr) == 1:
                    return State.WHERE
                # not 'WHERE {'?
                if len(parts_arr) == 2:
                    if new_part != "{":
                        raise Exception("Expected symbol '{' after WHERE but found " + f"'{parts_arr[1:]}'")
                    return State.WHERE
                # is 'WHERE { xxx' or 'WHERE { }'
                if len(parts_arr) == 3:
                    if new_part == "}":
                        return State.WHERE_END
                    return predict_state_inner_start(new_part)
                # not 'WHERE { }'
                if len(parts_arr) > 3:
                    raise Exception("Expected symbol '}' but got " + f"'{parts_arr[2:]}'")

            elif self.state == State.SUBJECT or \
                    self.state == State.PREDICATE or \
                    self.state == State.OBJECT:
                if len(parts_arr) == 0:
                    return self.state
                # term
                elif len(parts_arr) == 1:
                    return self.state
                # term ^^xsd:datatype OR term term
                elif len(parts_arr) == 2:
                    if str(parts_arr[1]).startswith(Const.dataTypeMark):
                        return self.state
                    if self.state == State.SUBJECT:
                        return State.PREDICATE
                    if self.state == State.PREDICATE:
                        return State.OBJECT
                    if self.state == State.OBJECT:
                        if parts_arr[1] == ".":
                            return self.state
                        return predict_state_inner_start(new_part)
                # term ^^xsd:datatype . OR term ^^xsd:datatype term
                elif len(parts_arr) == 3:
                    if self.state == State.SUBJECT:
                        return State.PREDICATE
                    if self.state == State.PREDICATE:
                        return State.OBJECT
                    if self.state == State.OBJECT:
                        # term ^^datatype .
                        if parts_arr[-1] == ".":
                            return self.state
                        return predict_state_inner_start(new_part)
                # term ^^xsd:datatype . term
                else:
                    if self.state == State.OBJECT:
                        return predict_state_inner_start(new_part)
                    raise Exception(f"Triplet can not be that long! '{parts_arr}' was attempted to be parsed "
                                    f"as {self.state.name}")

            elif self.state in [State.OPTIONAL, State.UNION]:
                if parts_arr[1] != "{":
                    raise Exception(f"{self.state.name} graph start " + "'{' not found. Parts: " + f"{parts_arr}")
                if len(parts_arr) > 3:
                    raise Exception(f"{self.state.name} graph seems deformed. Parts: " + f"{parts_arr}")
                if len(parts_arr) == 2:
                    return self.state
                if len(parts_arr) == 3:
                    return predict_state_inner_start(new_part)

            elif self.state == State.GRAPH_START:
                return predict_state_inner_start(new_part)

            elif self.state in [State.OPTIONAL_END,
                                State.UNION_END,
                                State.FILTER_END,
                                State.GRAPH_END]:
                return predict_state_inner_start(new_part)

            elif self.state in [State.WHERE_END, State.LIMIT, State.OFFSET]:
                return predict_state_after_where(new_part)

            elif self.state == State.ORDER_BY:
                if len(parts_arr) == 2:
                    if new_part == Const.by:
                        return self.state
                    raise Exception(f"Keyword 'ORDER' must be followed by 'BY' keyword. Found: {parts_arr}")
                return predict_state_after_where(new_part)

            elif self.state == State.FILTER:
                if parts_arr[1] != "(":
                    raise Exception(f"FILTER has no opening bracket '('? Found: {parts_arr}")
                if len(parts_arr) > 2:
                    return predict_state_inner_filter(new_part)
                return self.state

            elif self.state in [State.NEGATION,
                                State.LEFT_OPERAND,
                                State.OPERATOR,
                                State.RIGHT_OPERAND,
                                State.LOGICAL_UNKNOWN,
                                State.LOGICAL_AND,
                                State.LOGICAL_OR]:
                return predict_state_inner_filter(new_part)

            elif self.state == State.BOUND:
                if parts_arr[-2] != ")":
                    # why -2: we want a buffer
                    #   like        "BOUND ( ?q ) &"
                    #   not like    "BOUND ( ?q )"
                    return self.state
                return predict_state_inner_filter(new_part, is_allow_unsafe=True)

            return State.ERROR

        def clear_parts_arr(is_keep_last_part=False) -> None:
            if is_keep_last_part:
                to_save = parts_arr[-1]
                parts_arr.clear()
                parts_arr.append(to_save)
            else:
                parts_arr.clear()

        def set_state(state_new: State):
            self.state = state_new
            preserved_states_arr[-1] = self.state
            self.state_history_arr.append(state_new)

        def is_going_into_depth(state_new: State) -> bool:
            if self.state == State.WHERE and state_new != State.WHERE_END:
                return True
            if self.state == State.OPTIONAL and state_new != State.OPTIONAL_END:
                return True
            if self.state == State.UNION and state_new != State.UNION_END:
                return True
            if self.state == State.GRAPH_START and state_new != State.GRAPH_END:
                return True
            if self.state == State.FILTER and state_new != State.FILTER_END:
                return True
            return False

        def is_going_out_of_depth(state_new: State) -> bool:
            # there are preserved states
            if len(preserved_states_arr) > 1:
                if state_new in [State.WHERE_END,
                                 State.OPTIONAL_END,
                                 State.GRAPH_END,
                                 State.UNION_END,
                                 State.FILTER_END]:
                    return True
            return False

        def is_last_part_to_be_carried_in(state_new: State) -> bool:
            if state_new in [State.SUBJECT,
                             State.PREDICATE,
                             State.OBJECT,
                             State.OPTIONAL,
                             State.GRAPH_START,
                             State.NEGATION,
                             State.BOUND,
                             State.LEFT_OPERAND]:
                return True
            elif state_new in [State.WHERE_END,
                               State.UNION_END,
                               State.OPTIONAL_END,
                               State.GRAPH_END,
                               State.FILTER_END]:
                return False
            return False

        def is_last_part_to_be_carried_out(state_new: State) -> bool:
            if state_new in [State.WHERE_END,
                             State.OPTIONAL_END,
                             State.FILTER_END,
                             State.UNION_END,
                             State.GRAPH_END,
                             State.FILTER_END]:
                return True
            return False

        def preserve_state(state_new: State, carry_last_part: bool) -> None:
            # carry_last_part - is last part to be carried into new parts_arr?
            # adds state to states_arr
            # saves current parts_arr (with or without carry) as different pointer
            # makes parts_arr empty arr or arr with carried part
            preserved_states_arr.append(state_new)

            to_carry = State.ERROR
            if carry_last_part:
                to_carry = parts_arr.pop()

            preserved_parts_arr_arr[-1] = [*parts_arr]
            parts_arr.clear()

            if carry_last_part:
                parts_arr.append(to_carry)
            preserved_parts_arr_arr.append(parts_arr)

        def pop_state(state_new: State, carry_last_part: bool) -> None:
            # pops state from preserved ones
            # loads parts_arr (with or without carry)
            # sets new state
            if len(preserved_states_arr) < 2:
                raise Exception("Popping of state was called when there were no saved states (needs at least 2 states)")

            to_carry = State.ERROR
            if carry_last_part:
                to_carry = parts_arr.pop()

            preserved_parts_arr_arr.pop()
            preserved_states_arr.pop()

            parts_arr.clear()
            parts_arr.extend(preserved_parts_arr_arr[-1])

            if carry_last_part:
                parts_arr.append(to_carry)

            preserved_parts_arr_arr[-1] = parts_arr

        def process_parts_arr(state_next: State) -> None:
            # we come here when:
            # 1. no more stuff left to read
            # 2. we loaded one more keywoard that changed our state
            # 3. there is nothing to read
            state_now = preserved_states_arr[-1]
            if len(parts_arr) == 0:
                return
            if state_now == State.INIT:
                if len(parts_arr) != 1:
                    # hey, it is len > 0 in INIT. What is it?
                    raise Exception(f"Start of query did not recognised. First keyword '{parts_arr[0]}' was confusing")
                return

            elif state_now == State.PREFIX:
                if state_next != State.SELECT:
                    raise Exception(f"State {state_next.name} was unexpected after reading prefixes")
                elif (len(parts_arr) - 1) % 3 != 0:
                    raise Exception(f"One of prefixes might be corrupted! Check their syntax")
                # read each PREFIX name: <qqq>
                for i in range(2, len(parts_arr), 3):
                    if parts_arr[i - 2] != Const.prefix:
                        raise Exception(f"Expected prefixes in format 'PREFIX name: <qqq>' . Got in format "
                                        f"'{parts_arr[i - 2]} {parts_arr[i - 1]} {parts_arr[i]}'")
                    query.prefix_add(parts_arr[i - 1], parts_arr[i])  # name and <prefix>
                clear_parts_arr(is_keep_last_part=True)
                return

            elif state_now == State.SELECT:
                if parts_arr[0] != Const.select:
                    raise Exception(f"You have been in SELECT state without having a SELECT? Instead of 'SELECT', "
                                    f"found '{parts_arr[0]}'")
                if state_next != State.WHERE:
                    raise Exception(f"Cannot transit from SELECT state to {state_next.name} state")
                for i in range(1, len(parts_arr) - 1):
                    if parts_arr[i] == Const.distinct:
                        query.set_distinct(True)
                        continue
                    query.select_variable_add(parts_arr[i])
                clear_parts_arr(is_keep_last_part=True)
                return

            elif state_now == State.SUBJECT:
                # subject predicate
                if len(parts_arr) == 2:
                    query.triplet_set_subject(parts_arr[0])
                # subject ^^datatype predicate
                elif len(parts_arr) == 3:
                    query.triplet_set_subject(parts_arr[0], parts_arr[1])
                # mis-formed
                else:
                    raise Exception(f"SUBJECT '{parts_arr[0:-1]}' consists of unexpected term count: "
                                    f"{len(parts_arr) - 1}")
                clear_parts_arr(is_keep_last_part=True)
                return

            elif state_now == State.PREDICATE:
                # predicate object
                if len(parts_arr) == 2:
                    query.triplet_set_predicate(parts_arr[0])
                # predicate ^^datatype object
                elif len(parts_arr) == 3:
                    query.triplet_set_predicate(parts_arr[0], parts_arr[1])
                # mis-formed
                else:
                    raise Exception(f"PREDICATE '{parts_arr[0:-1]}' consists of unexpected term count: "
                                    f"{len(parts_arr) - 1}")
                clear_parts_arr(is_keep_last_part=True)
                return

            elif state_now == State.OBJECT:
                # object subject
                if len(parts_arr) == 2:
                    query.triplet_set_object(parts_arr[0])
                # object . subject OR object ^^datatype subject
                elif len(parts_arr) == 3:
                    if parts_arr[-2] == ".":
                        query.triplet_set_object(parts_arr[0])
                    else:
                        query.triplet_set_object(parts_arr[0], parts_arr[1])
                elif len(parts_arr) == 4:
                    query.triplet_set_object(parts_arr[0], parts_arr[1])
                # mis-formed
                else:
                    raise Exception(f"OBJECT '{parts_arr[0:-1]}' consists of unexpected term count: "
                                    f"{len(parts_arr) - 1}")
                clear_parts_arr(is_keep_last_part=True)
                query.triplet_flush_and_reset()
                return

            elif state_now == State.WHERE_END:
                # WHERE { }
                if parts_arr[2] == "}":
                    clear_parts_arr(is_keep_last_part=(len(parts_arr) != 3))
                    return
                else:
                    raise Exception("WHERE block was found to be malformed. WHERE block: " + f"{parts_arr}")

            elif state_now in [State.OPTIONAL_END, State.UNION_END]:
                # OPTIONAL { } OR UNION { }
                if len(parts_arr) == 4 and parts_arr[-2] == "}":
                    clear_parts_arr(is_keep_last_part=True)
                    return
                else:
                    raise Exception("Graph block was found to be malformed. Graph block: " + f"{parts_arr}")

            elif state_now == State.GRAPH_END:
                if len(parts_arr) == 3 and parts_arr[-2] == "}":
                    clear_parts_arr(is_keep_last_part=True)
                    return
                else:
                    raise Exception("Graph block seems to be melformed. Graph block: " + f"{parts_arr}")

            elif state_now == State.FILTER_END:
                # FILTER ( ) }
                if len(parts_arr) == 4 and parts_arr[-2] == ")":
                    clear_parts_arr(is_keep_last_part=True)
                    return
                else:
                    raise Exception("FILTER block was found to be malformed. FILTER block: " + f"{parts_arr}")

            elif state_now == State.LIMIT:
                if str(parts_arr[1]).isnumeric():
                    query.limit = int(parts_arr[1])
                    clear_parts_arr(is_keep_last_part=(len(parts_arr) != 2))
                else:
                    raise Exception(f"LIMIT by non numeric value is invalid. Value: {parts_arr[1]}")
                return

            elif state_now == State.OFFSET:
                if str(parts_arr[1]).isnumeric():
                    query.offset = int(parts_arr[1])
                    clear_parts_arr(is_keep_last_part=(len(parts_arr) != 2))
                else:
                    raise Exception(f"OFFSET by non numeric value is invalid. Value: {parts_arr[1]}")
                return

            elif state_now == State.ORDER_BY:
                if state_next == State.END:
                    query.set_order(parts_arr[2:])
                    clear_parts_arr(is_keep_last_part=False)
                else:
                    query.set_order(parts_arr[2:-1])
                    clear_parts_arr(is_keep_last_part=True)
                return

            elif state_now == State.LEFT_OPERAND:
                # no case of ! ?var
                # ?var1 >
                if len(parts_arr) == 2:
                    query.set_filter_left_operand(parts_arr[0])
                    clear_parts_arr(is_keep_last_part=True)
                    return

            elif state_now == State.NEGATION:
                # ! bound (
                if len(parts_arr) == 2:
                    query.set_filter_negation(True)
                    return

            elif state_now == State.BOUND:
                # bound ( ?q ) & OR ! bound ( ?q ) &
                if parts_arr[-4] != "(":
                    raise Exception(f"Function malformed: no opening bracket. Parts arr: {parts_arr}")
                if parts_arr[-2] != ")":
                    raise Exception(f"Function malformed: no closing bracket. Parts arr: {parts_arr}")
                arguments = parts_arr[-3:-2]
                if len(arguments) < 1:  # is it possible?
                    raise Exception(f"Function malformed: no arguments found. Parts arr: {parts_arr}")
                if parts_arr == "!":
                    query.set_filter_negation(True)
                query.set_filter_function(Const.bound)
                query.set_filter_function_arguments([arguments[0]])
                clear_parts_arr(is_keep_last_part=True)
                return

            elif state_now == State.OPERATOR:
                # < ?var2
                if len(parts_arr) == 2:
                    query.set_filter_operator(parts_arr[0])
                # < = ?var2
                elif len(parts_arr) == 3:
                    query.set_filter_operator(parts_arr[0] + parts_arr[1])
                else:
                    raise Exception(f"Malformed operator. Parts arr: {parts_arr}")
                clear_parts_arr(is_keep_last_part=True)
                return

            elif state_now == State.RIGHT_OPERAND:
                # ?var2 & OR ?var2 )
                # no case of ! ?var2 &
                if len(parts_arr) == 2:
                    query.set_filter_right_operand(parts_arr[-2])
                    clear_parts_arr(is_keep_last_part=True)
                    return

            elif state_now == State.LOGICAL_UNKNOWN:
                return

            elif state_now == State.LOGICAL_AND:
                # & & ?var1
                query.filter_condition_flush()
                query.filter_condition_new(Const.opLogicalAnd)
                clear_parts_arr(is_keep_last_part=True)
                return

            raise Exception(f"No processing instructions were found for state {state_now.name}. "
                            f"\nParts arr: {parts_arr}")

        def is_graph_to_be_stepped(state_now: State, state_new: State) -> bool:
            return state_now in [State.UNION,
                                 State.OPTIONAL,
                                 State.WHERE,
                                 State.GRAPH_START] \
                or state_new in [State.UNION_END,
                                 State.OPTIONAL_END,
                                 State.GRAPH_END]
            # WHERE_END is not needed. WHERE creates root graph

        def set_graph_properties(state_next: State) -> None:
            if state_next == State.OPTIONAL_END:
                query.graph_temp.is_optional = True
            elif state_next == State.UNION_END:
                query.graph_temp.is_union = True

        while True:
            part = get_next_part()
            if is_part_empty(part):
                process_parts_arr(State.END)
                break

            state_prediction = predict_state()
            if self.state != state_prediction and state_prediction != State.ERROR:
                # example: WHERE -> SUBJECT
                if is_going_into_depth(state_prediction):
                    preserve_state(state_prediction, is_last_part_to_be_carried_in(state_prediction))
                    if is_graph_to_be_stepped(self.state, state_prediction):
                        query.graph_create_and_step_in()
                else:
                    process_parts_arr(state_prediction)
                # example: OBJECT -> WHERE_END
                if is_going_out_of_depth(state_prediction):
                    pop_state(state_prediction, is_last_part_to_be_carried_out(state_prediction))
                    set_graph_properties(state_prediction)
                    if is_graph_to_be_stepped(self.state, state_prediction):
                        query.graph_step_out()
                set_state(state_prediction)

            elif state_prediction == State.ERROR:
                raise Exception("Error in predicting next state. "
                                f"\nCurrent state: {self.state.name}"
                                f"\nPredicted state: {state_prediction.name}"
                                f"\nCurrent parts arr: {parts_arr}"
                                f"\nPreserved states arr: {preserved_states_arr}"
                                f"\nPreserved parts arr arr: {preserved_parts_arr_arr}")
        return query
