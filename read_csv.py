#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import re
import csv
import collections
import pandas as pd
from tkinter import messagebox


def operand_type(string):
    if string.isdigit(): # decimal number
        return "dec_num"
    elif re.complie("0x[0-9a-fA-F]+").match(string): # hexadecimal number
        return "hex_num"
    else: # string case
        return "string"


def readCsv(filename):
    # find valid indexes for the convenience of reading the whole csv using pandas
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            col_list = row
            break
    while col_list[-1]=='':
        col_list.pop()
    #print (col_list)
    col_num = len(col_list)
    #print (col_num)


    # if the head has blank in it, it may be troublesome in the following process
    need_change = False
    for head in col_list:
        if len(head.split(' '))!=1:
            messagebox.showwarning("警告", message="csv文件中有列表项存在空格，自动将以_填充")
            need_change = True
            break
    if need_change:
        new_col_list = []
        for head in col_list:
            if len(head.split(' '))!=1:
                new_col_list.append('_'.join(head.split(' ')))
            else:
                new_col_list.append(head)
        col_list = new_col_list


    # Read valid columns. Notice here type are seen as string for convenience
    df = pd.read_csv(filename, usecols=[i for i in range(col_num)], dtype=str, encoding="gb2312")
    if need_change:
        tmp_df = pd.DataFrame(df.values, columns=col_list)
        tmp_df.to_csv(filename, index=False)
        df = tmp_df
    print (df)

    type_list = []
    sample = df.iloc[0]
    for item in sample:
        print ([item, operand_type(item)])
        type_list.append(operand_type(item))

    col_type = collections.OrderedDict()
    for i in range(len(col_list)):
        col_type[col_list[i]] = type_list[i]
    print (col_type)


    # replace '-' with formal data. '-' means the same as last row
    (row, col) = df.shape
    for i in range(row):
        line = df.iloc[i]
        if line[0]=='-':
            for j in range(col):
                if line[j]!='-':
                    break
                line[j] = df.iloc[i-1][j]

    return {"df":df, "col_type":col_type}


if __name__ == "__main__":
    filename = ""
    readCsv(filename)




