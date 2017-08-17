# -*- coding:utf-8 -*-

import operator


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






class judge:
    def __init__(self,expression):
        self.expression = expression
