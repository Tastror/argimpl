from typing import Optional, Tuple, Any
from pyparsing import alphas, nums, alphanums, printables
from pyparsing import Regex, Literal, Word, Combine, Optional, OneOrMore, ZeroOrMore, Group, Suppress, White, ParseResults

# TODO: make this safer and more accurate

boolean = Regex("([tT]rue|[fF]alse)")
integer = Regex("([+-]?[0-9]+)")
str = Regex('("(?:[^"]|\\")*?")') ^ Regex("('(?:[^']|\\')*?')")
atomic = boolean ^ integer ^ str

list_0 = Literal("[") + Literal("]")
list_gt0 = Literal("[") + atomic + ZeroOrMore(Literal(",") + atomic) + Optional(Literal(",")) + Literal("]")
list_single_dim = list_0 ^ list_gt0
list_multi_dim_gt0 = Literal("[") + (atomic ^ list_single_dim) + ZeroOrMore(Literal(",") + (atomic ^ list_single_dim)) + Optional(Literal(",")) + Literal("]")
lister = list_0 ^ list_multi_dim_gt0

head_sin_operator = Literal("!").setParseAction(lambda _: "not ") ^ Literal("-")
sin_operator = Literal(".len").setParseAction(lambda _: ".__len__()")
bin_operator = Literal("+") ^ Literal("-") ^ Literal("*") ^ Literal("//") ^ Literal("%")

single_expression = ((OneOrMore(head_sin_operator) + atomic) ^ (lister + OneOrMore(sin_operator)) ^ (atomic + OneOrMore(bin_operator + atomic)) ^ \
                    (lister + OneOrMore(Literal("[") + atomic + Literal("]")))) | (atomic ^ lister)
unbracket_unit = single_expression
bracket_unit = Literal("(") + single_expression + Literal(")")
unit = unbracket_unit ^ bracket_unit
expression = \
    ((OneOrMore(head_sin_operator) + unit).setResultsName("head_sin") ^ \
    (unit + OneOrMore(sin_operator)).setResultsName("sin") ^ \
    (unit + OneOrMore(bin_operator + unit)).setResultsName("bin") ^ \
    (lister + OneOrMore(Literal("[") + unit + Literal("]"))).setResultsName("[]")) | unit.setResultsName("unit")


def safe_eval(str_to_parse: str) -> Tuple[Any, bool]:
    try:
        # check
        str_to_parse = " ".join(expression.parseString(str_to_parse))
        print(str_to_parse)
        s = eval(str_to_parse)
        return s, True
    except Exception:
        return None, False


if __name__ == "__main__":

    print(boolean.parseString("true"))
    print(boolean.parseString("false"))
    try:
        print(boolean.parseString("123"))
        print("error passed!")
    except Exception as e:
        print("OK, not pass")
    
    print(integer.parseString("123"))
    print(integer.parseString("+456"))
    print(integer.parseString("-0789"))
    try:
        print(integer.parseString("+-1"))
        print("error passed!")
    except Exception as e:
        print("OK, not pass")

    print(str.parseString("''"))
    print(str.parseString("'12_$ &*(V\t\n *H#(3'"))
    print(str.parseString('"+4 5 6"'))
    print(str.parseString("'''-0789'''"))
    try:
        print(integer.parseString("[]"))
        print("error passed!")
    except Exception as e:
        print("OK, not pass")

    print(lister.parseString("[]"))
    print(lister.parseString("[ ]"))
    print(lister.parseString("[true]"))
    print(lister.parseString("[[]]"))
    print(lister.parseString("['123',]"))
    print(lister.parseString("[true, '123', false, [], [1, 2], -12]"))
    try:
        print(lister.parseString("[true, '123', false, [],, [1, 2], -12]"))
        print("error passed!")
    except Exception as e:
        print("OK, not pass")

    print(expression.parseString("[true, '123', false, [], [1, 2], -12][4][0] + (-5 * 8) % (7 - 8) // 2"))
    print(expression.parseString("['apple','banana','orange'][0]+'_and_'+['apple','banana','orange'][1]"))
    print(expression.parseString("['banana', 'pear'].len * 5"))
    try:
        print(lister.parseString("import os"))
        print("error passed!")
    except Exception as e:
        print("OK, not pass")