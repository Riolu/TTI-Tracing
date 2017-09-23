#!/usr/bin/env python
#  -*- coding:utf-8 -*-

from read_csv import *

import re
import time
import operator
import collections


class RuleError(Exception):
    def __init__(self, err):
        Exception.__init__(self)
        self.err = err

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



    def modify(self):
        expr_list = self.expression.strip().split('\n')
        print ("Original rules \t", expr_list)

        # split the parentheses with other characters for convenience
        new_list = []
        parentheses = ['(',')','[',']']
        for rule in expr_list:
            for seq in parentheses:
                split_list = rule.split(seq)
                for i in range(len(split_list)):
                    split_list[i] = split_list[i].strip(' ')
                new_seq = ' '+seq+' '
                rule = new_seq.join(split_list)
            new_list.append(rule)

        # delete empty rules
        tmp_list = new_list.copy()
        for rule in tmp_list:
            if whitespace(rule) or rule=='':
                new_list.remove(rule)

        self.rules = new_list
        print ("Modified rules \t", self.rules, '\n')



    # here slice the rule and simulate read_rule() for every single rule for each row
    # the reason to split the expression into rules is that this small part can be included in the err_list if wrong
    def judge(self):
        (df_row, df_col) = Expr.df.shape

        for rule in self.rules:
            self.err_rule_dict[rule] = []

        #df_row = 5 # this is used for test
        for row in range(df_row):
            print ("This is", row, "row!")
            for rule in self.rules:
                if not self.read_rule(rule, row):
                    if row not in self.err_row_dict:
                        self.err_row_dict[row] = []

                    self.err_row_dict[row].append(rule)
                    self.err_rule_dict[rule].append(row)

        # delete rules which is correct for all
        tmp_dict = self.err_rule_dict.copy()
        for k, v in tmp_dict.items():
            if len(v) == 0:
                self.err_rule_dict.pop(k)

        print ('\n')
        print (self.err_row_dict)
        print (self.err_rule_dict)
        print ("======================================\n")



    def show(self):
        print (self.expression)



    # 中缀表达式
    # 依次读入表达式每一项
    # 操作数 压入操作数栈
    # 操作符 考虑当前操作符与操作符栈顶的符号 出栈知道当前优先级高于栈顶的优先级
    # ( 继续
    # ) 出栈知道左括号
    #
    # read a rule in a certain line, and the result must be boolean
    def read_rule(self, str, row):
        opStack  = Stack()  # operator stack
        numStack = Stack()  # operand stack
        pos = 0

        while pos < len(str):
            token, pos, token_type = self.get_token(str, pos)
            if token.element == "":  # for cases that the blank appears in the end
                break
            token.show()

            if token_type == 1: # if the token is with a condition, use the read_rule() recursively to process the condition expression
                [condition, rule_with_cond] = token.element.split('$')
                print ("deal with conditon: " + condition)
                condition_res = self.read_rule(condition, row)
                #print (condition_res)
                if condition_res == False: # condition not satisfied, skip
                    print ("Condition " + condition + " not satisfied.")
                    numStack.push( Token(int(True)) )
                else:
                    print ("Condition " + condition + " is satisfied. Now move on.")
                    numStack.push( Token(int(self.read_rule(rule_with_cond))) )
                continue

            if token_type == 2: # if the token is a function
                [func, parameter] = token.element.split('$')
                func = func.strip()
                if parameter not in self.count_reserved:
                    self.count_reserved[parameter] = {}
                    count_reserved_dict = self.count_reserved[parameter]
                    count_reserved_dict["func_res"] = 0
                    count_reserved_dict["nextrow"]  = 0

                count_reserved_dict = self.count_reserved[parameter]
                if row == count_reserved_dict["nextrow"]: # this means another tick starts, or the func_res and nextrow remain the same
                    count_reserved_dict["func_res"], count_reserved_dict["nextrow"] = Token.function[func](self, parameter, row)

                print ("function result:", count_reserved_dict["func_res"], "\t nextrow:", count_reserved_dict["nextrow"])
                numStack.push( Token(count_reserved_dict["func_res"]) )
                continue


            if token.isoperand:
                numStack.push(token_type)
            else:
                #print (token.element)
                if token.element == '(':
                    opStack.push(token)

                elif token.element == ')':
                    while not opStack.empty() and (opStack.top()).element != '(':
                        tmp_op = opStack.top()
                        opStack.pop()
                        num2 = numStack.top()
                        numStack.pop()
                        num1 = numStack.top()
                        numStack.pop()
                        result = self.cal(num1, num2, tmp_op, row)
                        numStack.push(result)
                    opStack.pop() # pop corresponding '('

                else:
                    while not opStack.empty() and self.operand_pri(token, opStack.top())<=0: #priority[cur_op]<=priority[opStack.top()]
                        tmp_op = opStack.top()
                        opStack.pop()
                        num2 = numStack.top()
                        numStack.pop()
                        num1 = numStack.top()
                        numStack.pop()
                        result = self.cal(num1, num2, tmp_op, row)
                        numStack.push(result)
                    opStack.push(token)

        while not opStack.empty():
            tmp_op = opStack.top()
            opStack.pop()
            num2 = numStack.top()
            numStack.pop()
            num1 = numStack.top()
            numStack.pop()
            result = self.cal(num1, num2, tmp_op, row)
            numStack.push(result)

        return bool( numStack.top().element )








    # 分为两类 操作数和操作符
    # 操作数 分为 字符串 10进制数 16进制数
    # 操作符 分为 基本 比较 逻辑操作符 其他（括号）
    # 如果带条件 则将条件与该条件约束的表达式当做一个token
    # 如果是函数 整体当做一个token

    # The function skips the whitespaces and captures a continuous string
    # for Condition or Function, the whole Condition or Function is read as one token
    def get_token(self, str, pos):
        token_type = 0  # 0-normal token  1-token with condition  3-token of function
        while pos<len(str) and whitespace(str[pos]):  # skip the whitespace
            pos = pos + 1
            if pos == len(str):
                return Token(""), pos, token_type

        curstr = ""

        # this is the beginning sign of the condition
        if str[pos]=='[':
            token_type = 1
            pos = pos+1
            while pos<len(str) and str[pos]!=']':
                curstr = curstr + str[pos]
                pos = pos + 1
            pos = pos +1 # skip ']'

            curstr = curstr + " $ "

            while pos<len(str) and whitespace(str[pos]):
                pos = pos + 1

            if str[pos]=='(': # find pairing ')'
                pos = pos + 1
                left_count = 1
                while pos<len(str):
                    if str[pos]=='(':
                        left_count = left_count + 1
                    if str[pos]==')':
                        left_count = left_count - 1
                    if left_count==0:
                        break
                    curstr = curstr + str[pos]
                    pos = pos +1
                pos = pos + 1 #skip ')'

            else: # this is a global condition
                curstr = curstr + str[pos:]
                pos = len(str) # next character to read is out of index

            # now the curstr is of a $ b form where a is the condition while b is the content


        else:
            while pos<len(str) and not whitespace(str[pos]): # get a continuous string
                curstr = curstr + str[pos]
                pos = pos + 1

        #print (curstr)

        if curstr in Token.function: # the curstr is the function name
            token_type = 2
            function_content, pos = self.get_content(str, pos)
            curstr = curstr + ' $ ' + function_content


        token = Token(curstr)
        return token, pos, token_type



    # 运算符优先级比较
    # token1>token2 return 1
    # token1=token2 return 0
    # token1<token2 return -1
    def operand_pri(self, token1, token2):
        prior = Token.general_pri
        if prior[token1.type] > prior[token2.type]:
            return 1
        elif prior[token1.type] < prior[token2.type]:
            return -1
        else: # same type
            if token1.type == "comop":
                return 0

            dic = eval("Token."+token1.type+"_pri")
            #print (dic)
            if dic[token1.element]>dic[token2.element]:
                return 1
            elif dic[token1.element]<dic[token2.element]:
                return -1
            else:
                return 0



    def valid_cal(self,type1, type2):
        if type1 == type2:
            return True
        if type1=="dec_num" and type2=="hex_num"  or  type1=="hex_num" and type2=="dec_num":
            return True
        return False



    def replace_with_csv(self, token, row): # the token's type is "head"
        col_type = Expr.col_type
        df = Expr.df
        cor_element = df.iloc[row][token.element] # this is string reading from csv
        #print (cor_element)
        return Token(cor_element)



    def cal(self, num1, num2, cur_op, row, condition=None): # all of the parameters are of the token form
        print (cur_op.element, num1.element, num2.element)

        if num1.type == "head":
            num1 = self.replace_with_csv(num1, row)
            print (cur_op.element, num1.element, num2.element)
        if num2.type == "head":
            num2 = self.replace_with_csv(num2, row)
            print (cur_op.element, num1.element, num2.element)

        # first we should judge whether type are the same
        if not self.valid_cal(num1.type, num2.type):
            print (num1.type, num2.type)
            print ("Errors occurred in the rule.")
            raise RuleError("not the same type")

        # calculate according to the type
        if num1.type == "hex_num" or num2.type == "hex_num":
            num1_dec = Token(int(num1.element,16)) if num1.type=="hex_num" else num1
            num2_dec = Token(int(num2.element,16)) if num2.type=="hex_num" else num2

            for op in Token.ops:
                if cur_op.element in eval("Token."+op):
                    ans = eval("Token."+op)[cur_op.element](num1_dec.element, num2_dec.element)
                    if isinstance(ans, bool): # simplify bool type
                        ans = int(ans)
                    else:
                        ans = hex(ans)
                    print (ans)
                    return Token(ans)

        if num1.type == "dec_num":
            for op in Token.ops:
                if cur_op.element in eval("Token."+op):
                    ans = eval("Token."+op)[cur_op.element](num1.element, num2.element)
                    if isinstance(ans, bool):
                        ans = int(ans)
                    print (ans)
                    return Token(ans)

        if num1.type == "string":
            if cur_op.element == "==":
                ans = num1.element==num2.element
                ans = int(ans)
                print (ans)
                return Token(ans)



    def get_content(self, str, pos): # this function is to find content content between ()
        while pos<len(str) and whitespace(str[pos]):
            pos = pos + 1

        curstr = ""
        if str[pos] == '(': # skip '('
            pos = pos + 1
            left_count = 1
            while pos<len(str):
                if str[pos]=='(':
                    left_count = left_count + 1
                if str[pos]==')':
                    left_count = left_count - 1
                if left_count==0:
                    break
                curstr = curstr + str[pos]
                pos = pos + 1
            pos = pos + 1 # skip ')'
        return curstr, pos





















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
