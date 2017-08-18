# -*- coding:utf-8 -*-

import operator
import re
import collections


class Stack:
    def __init__(self):
        self.items = []

    def empty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def top(self):
        if not self.empty():
            return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)


def mod(a, b):
    return a % b

def andand(a, b):
    if a!=0 and b!=0:
        return 1
    else:
        return 0

def oror(a, b):
    if a!=0 or b!=0:
        return 1
    else:
        return 0

def whitespace(a):
    white_space = [' ', '\t', '\n', '\v', '\r', '\f']
    if a in white_space:
        return True
    else:
        return False




class Expr:
    df = None
    col_type = None

    def __init__(self, expression, filename):
        self.expression = expression
        self.modify()

        csv_dict = readCsv(filename)
        Expr.df = csv_dict["df"]
        Expr.col_type = csv_dict["col_type"]

        self.err_row_dict  = collections.OrderedDict()  # result list according to row
        self.err_rule_dict = collections.OrderedDict()  # result list according to rule

        self.count_reserved = {}  # used to save variables for count function




class Token:
    ops = ["ordop", "compop", "logicop"]

    # ordinary opeartor
    ordop = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "%": mod,
        "^": operator.pow
    }

    # compare operator
    compop = {
        "==": operator.eq,
        "=": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
    }

    # logical operator
    logicop = {
        "&&": andand,
        "||": oror
    }

    extraop = {
        "(": "left",
        ")": "right"
    }


    # The following is the priority of the operators
    general_pri = {
        "ordop": 3,
        "compop": 2,
        "logicop": 1,
        "left": 0
    }

    ordop_pri = {
        "^": 3,
        "*": 2,
        "/": 2,
        "%": 2,
        "+": 1,
        "-": 1,
    }

    logicop_pri = {
        "&&": 2,
        "||": 1
    }

    # function = {
    #
    # }


    def __init__(self, str):
        # if int, directly create the object for convenience
        if isinstance(str, int):
            self.isoperand = 1
            self.type = "dec_num"
            self.element = str # here the element of int type

        #============== string cases ==============
        # operators
        for item in Token.ops:
            if str in eval("Token."+item):
                self.isoperand = 0
                self.type = item
                self.element = str
                return

        if str in Token.extraop:
            self.isoperand = 0
            self.type = Token.extraop[str]
            self.element = str

        # operand
        else:
            self.isoperand = 1
            [type, element] = self.operand_transfer(str)
            self.type = type
            self.element = element


    def operand_transfer(self, str): # if the operand is string, it may be the head of the csv file
        if str.isdigit(): # decimal number
            return ["dec_num", int(str)]
        elif re.compile("^0x[0-9a-fA-F]+").match(str): # hexadecimal number
            return ["hex_num", hex(int(str, 16))]
        else: # string case
            # col_type = Expr.col_type
            # if str in col_type: # the string is the head of the csv
            #     return ["head", str]
            # else:
                return ["string", str]
            # Notice str case includes many circumstances such as expression with condition and function


    def show(self):
        print (self.isoperand, '\t', self.type, '\t', self.element)




class judge:
    def __init__(self,expression):
        self.expression = expression



if __name__ == "__main__":
    a = Token("+")
    a.show()
