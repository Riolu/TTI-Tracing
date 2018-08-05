#!/usr/bin/env python
#  -*- coding:utf-8 -*-

from deal_rules import Expr
from deal_rules_multiple import Expr_multi
from read_csv import readCsv

import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.filedialog import *
from tkinter import messagebox
import win32clipboard as win
import win32con


def cur_file_dir(): # 获取脚本文件的当前路径
    path = sys.path[0] # 获取脚本路径
    # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

def getText():
    win.OpenClipboard()
    d = win.GetClipboardData(win32con.CF_UNICODETEXT)
    win.CloseClipboard()
    return d

def setText(aString):
    win.OpenClipboard()
    win.EmptyClipboard()
    win.SetClipboardData(win32con.CF_UNICODETEXT, aString)
    win.CloseClipboard()


class Application(tk.Tk):
    def __init__(self):
        super().__init__() # 有点相当于tk.Tk()

        self.title("Analytical Tools for TTI Trace")
        # self.title("TTI追踪对比分析工具")
        self.resizable(width=False, height=False)
        self.columnconfigure(0, minsize=50)

        self.frames = {}
        for F in (Single, Multi):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew") # 四个页面的位置都是 grid(row=0, column=0)，位置重叠，只有最上面的可见！！

        # self.show_frame(Single)
        # self.curframe_name = Single
        # self.curframe = self.frames[self.curframe_name]

        self.show_frame(Multi)
        self.curframe_name = Multi
        self.curframe = self.frames[self.curframe_name]


        self.project_dir = cur_file_dir()
        self.csv_dir = self.project_dir + "\\csv"
        self.rule_dir = self.project_dir + "\\rule"
        self.result_dir = self.project_dir + "\\result"
        if not os.path.exists(self.csv_dir):
            os.makedirs(self.csv_dir)
        if not os.path.exists(self.rule_dir):
            os.makedirs(self.rule_dir)
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)



    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise() # 切换，提升当前 tk.Frame z轴顺序（使可见）！！
        self.curframe_name = cont
        self.curframe = self.frames[cont]
        MyMenu(self) # refresh MyMenu so that open file can work correctly



    def addmenu(self, Menu):
        '''添加菜单'''
        Menu(self)



class Single(tk.Frame):
    '''第一页'''
    def __init__(self, parent, root):
        super().__init__(parent)
        self.createWidgets()
        self.root = root
        self.result_type = "row"



    def createWidgets(self):
        topframe = tk.Frame(self, width=580, height=50)
        topframe.pack(side=tk.TOP)
        ruleframe = tk.Frame(self, width=580, height=230) # 由于元素使用pack这里必须设定width和height 否则frame不会显示
        ruleframe.pack(side=tk.TOP)
        resultframe = tk.Frame(self, width=580, height=420) # 580 350
        resultframe.pack(side=tk.TOP)

        # 顶部区域
        glabel = tk.Label(topframe, text="Target file:")
        self.entryvar = tk.StringVar()
        gentry = tk.Entry(topframe, textvariable=self.entryvar, width=25)
        gbutton = tk.Button(topframe, command=self.__openfile, text='...')

        headlabel = tk.Label(topframe, text="Head")
        self.head_keyvar = tk.StringVar()
        self.head_keyvar.set("Title in CSV")
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.headcombobox = ttk.Combobox()





        # -- 放置位置
        glabel.grid(row=0, column=0, sticky=tk.W)
        gentry.grid(row=0, column=1)
        gbutton.grid(row=0, column=2)

        # -- 绑定事件
        gentry.bind('<Return>', func=self.__refresh)



        # 中部rule区域
        rulelabel = tk.Label(ruleframe, text="Please input the judge rules")
        ruletext_frame = tk.Frame(ruleframe) # 放rule_text和rule_rightbar, rule_bottombar
        rule_rightbar = tk.Scrollbar(ruletext_frame, orient=tk.VERTICAL)
        rule_bottombar = tk.Scrollbar(ruletext_frame, orient=tk.HORIZONTAL)
        self.rule_text = tk.Text(ruletext_frame, width=80, height=10, yscrollcommand=rule_rightbar.set, xscrollcommand=rule_bottombar.set, wrap="none") # 设置滚动条 - 不换行
        # font = {"宋体"，12, "normal"}
        headlabel = tk.Label(ruleframe, text="Field Name")
        self.head_keyvar = tk.StringVar()
        self.head_keyvar.set("Title in CSV")
        self.headcombobox = ttk.Combobox(ruleframe, values=["Empty"], textvariable=self.head_keyvar, state="disabled")
        headbutton = tk.Button(ruleframe, text="Add", command=self.__add_head)
        clearbutton= tk.Button(ruleframe, text="  Clear  ", command=self.__clear_rule)
        rulebutton = tk.Button(ruleframe, text="Analyze", command=self.__analyze)

        # -- 放置位置
        rule_rightbar.pack(side=tk.RIGHT, fill=tk.Y)
        rule_bottombar.pack(side=tk.BOTTOM, fill=tk.X)
        self.rule_text.pack(side=tk.LEFT, fill=tk.BOTH)

        rulelabel.place(x=0, y=0)
        ruletext_frame.place(x=0, y=20)

        headlabel.place(x=5, y=int(ruletext_frame.place_info()['y'])+165)
        self.headcombobox.place(x=80, y=int(headlabel.place_info()['y']))
        headbutton.place(x=250, y=int(headlabel.place_info()['y'])-5)
        clearbutton.place(x=440, y=int(headlabel.place_info()['y'])-5)
        rulebutton.place(x=510, y=int(headlabel.place_info()['y'])-5)

        # -- 绑定事件
        rule_rightbar.config(command=self.rule_text.yview)
        rule_bottombar.config(command=self.rule_text.xview)
        self.rule_text.bind('<Button-3>', func=self.__popup)



        # 结果区域
        result_label = tk.Label(resultframe, text="Analysis Result")
        resulttext_frame = tk.Frame(resultframe) # 放rule_text和rule_rightbar
        result_rightbar = tk.Scrollbar(resulttext_frame, orient=tk.VERTICAL)
        result_bottombar = tk.Scrollbar(resulttext_frame, orient=tk.HORIZONTAL)
        self.result_text = tk.Text(resulttext_frame, width=80, height=20, yscrollcommand=result_rightbar.set, xscrollcommand=result_bottombar.set, wrap="none")
        self.switchbutton = tk.Button(resultframe, text="Switch Result", command=self.switch_result, state="disabled")

        # -- 放置位置
        result_rightbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_bottombar.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH)

        result_label.place(x=0, y=0)
        resulttext_frame.place(x=0, y=20)
        self.switchbutton.place(x=478, y=310)

        # -- 绑定事件
        result_rightbar.config(command=self.result_text.yview)
        result_bottombar.config(command=self.result_text.xview)


        edit_items = ['Cut', 'Copy', 'Paste', 'Delete']
        self.Rbtnmenubar = tk.Menu(self, tearoff=0)
        self.Rbtnmenubar.add_command(label=edit_items[0], command=self.__cut_clk)
        self.Rbtnmenubar.add_command(label=edit_items[1], command=self.__copy_clk)
        self.Rbtnmenubar.add_command(label=edit_items[2], command=self.__paste_clk)
        self.Rbtnmenubar.add_command(label=edit_items[3], command=self.__delete_clk)


    def __popup(self, event): # 右键弹出
        self.Rbtnmenubar.post(event.x_root, event.y_root)

    def __cut_clk(self): # 剪切右键的回调
        try:
            setText(self.rule_text.get(SEL_FIRST,SEL_LAST))
            self.rule_text.delete(SEL_FIRST,SEL_LAST)
        except: pass

    def __copy_clk(self): # 复制右键的回调
        try:
            setText(self.rule_text.get(SEL_FIRST,SEL_LAST))
        except: pass

    def __paste_clk(self): # 粘贴右键的回调
        self.rule_text.insert(INSERT, getText())

    def __delete_clk(self): #剪切右键的回调
        try:
            self.rule_text.delete(SEL_FIRST,SEL_LAST)
        except: pass


    def __openfile(self):
        self.filename = filedialog.askopenfilename(title="Open File", initialdir=self.csv_dir, filetypes=[('CSV File','*.csv'),('All Files','*')])
        self.entryvar.set(self.filename)

        if not self.filename:
            pass
        else:
            try:
                col_type = readCsv(self.filename)["col_type"]
                self.head_keyvar.set("Title in CSV")
                self.headcombobox["values"] = list(col_type.keys()) # modify the combobox after csv is read
                self.headcombobox["state"] = "normal"
                self.result_text.delete('1.0', tk.END)
                self.result_text.insert(tk.END, "Loaded " + self.filename + "\n\n")
            except:
                messagebox.showerror("Error", message="The file cannot be opened, please try again.")

    def __refresh(self):
        self.filename = self.entryvar.get()
        # self.textbox.insert(tk.END, self.filename+"\r\n")
        # self.textbox.update()

    def __analyze(self):
        self.rule = self.rule_text.get('1.0', tk.END)
        if self.rule=='\n':
            messagebox.showwarning("Warning", message="Please Input the Judge Rules!")
        else:
            try:
                a = Expr(self.rule, self.filename)
                a.judge()
                err_row_dict = a.err_row_dict
                err_rule_dict = a.err_rule_dict

                # 分析结果 以row为顺序
                self.result_row_str = "Current File:" + self.filename + "\n\n"
                if len(err_row_dict)==0:
                    self.result_row_str = self.result_row_str + "No Error!\n"
                else:
                    for row, row_list in err_row_dict.items():
                        self.result_row_str = self.result_row_str + "Error Line:" + str(row+2) + "\n" # 对应csv中行号
                        for err_rule in row_list:
                            self.result_row_str = self.result_row_str + "Error Rule:" + err_rule + "\n"
                        self.result_row_str = self.result_row_str + "\n"



                # 分析结果 以rule为顺序
                self.result_rule_str = "Current File:" + self.filename + "\n\n"
                if len(err_row_dict)==0:
                    self.result_rule_str = self.result_rule_str + "No Error!\n"
                else:
                    for rule, rule_list in err_rule_dict.items():
                        self.result_rule_str = self.result_rule_str + "Error Rule:" + rule + "\n"
                        for err_row in rule_list:
                            self.result_rule_str = self.result_rule_str + "Error Line:" + str(err_row+2) + "\n"
                        self.result_rule_str = self.result_rule_str + "\n"

                self.result_text.delete('1.0', tk.END)
                self.result_text.insert(tk.END, self.result_row_str+"\n")

                self.switchbutton["state"] = "normal"

            except:
                messagebox.showerror("Warning", message = "The judging rule seems to have some error, please revise it and try again.")


    def __add_head(self):
        head = self.headcombobox.get()
        if head=="Title in CSV":
            messagebox.showwarning("Warning", message="No head is chosen!")
        else:
            self.rule_text.insert(tk.END, head+" ")

    def __clear_rule(self):
        self.rule_text.delete("1.0", tk.END)

    def switch_result(self):
        if self.result_type=="row":
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, self.result_rule_str+"\n")
            self.result_type = "rule"
        else:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, self.result_row_str + "\n")
            self.result_type = "row"





class MyMenu():
    # 菜单类

    def __init__(self, root):
        # 初始化菜单
        self.menubar = tk.Menu(root) # 创建菜单栏
        self.root = root # root是Application的一个实例 由于command如果带()回自动执行，因此将root保存为MyMenu的对象

        # 创建“File”下拉菜单
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Open File", command=self.file_open)
        filemenu.add_separator()
        filemenu.add_command(label="Open Rule", command=self.rule_open)
        filemenu.add_command(label="Save Rule", command=self.rule_save)
        filemenu.add_separator()
        filemenu.add_command(label="Save Result", command=self.result_save)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=root.quit)

        # 创建“Help”下拉菜单
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.help_about)

        # 将前面两个菜单加到菜单栏
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.menubar.add_cascade(label="Help", menu=helpmenu)

        # 最后再将菜单栏整个加到窗口 root
        root.config(menu=self.menubar)


    def file_open(self):
        self.root.filename = filedialog.askopenfilename(title="Open File", initialdir=self.root.csv_dir, filetypes=[('CSV File', '*.csv'), ('All Files', '*')])
        self.root.entryvar.set(self.root.filename)

        if not self.root.filename:
            pass
        else:
            try:
                col_type = readCsv(self.root.filename)["col_type"]
                self.root.head_keyvar.set("Title in CSV")
                self.root.headcombobox["values"] = list(col_type.keys())  # modify the combobox after csv is read
                self.root.headcombobox["state"] = "normal"
                self.root.result_text.delete('1.0', tk.END)
                self.root.result_text.insert(tk.END, "Loaded " + self.root.filename + "\n\n")
            except:
                messagebox.showerror("Error", message="The file cannot be opened, please try again.")


    def rule_open(self):
        rule_name = askopenfilename(title="Open Rule", initialdir=self.root.rule_dir, filetypes=[("Text File",'*.txt')])
        if rule_name:
            rule_file = open(rule_name, "r")
            rule_content = rule_file.read()
            rule_file.close()
            self.root.rule_text.delete("1.0", tk.END)
            self.root.rule_text.insert("1.0", rule_content)

    def rule_save(self):
        rule_name = asksaveasfilename(title="Save Rule", initialdir=self.root.rule_dir, filetypes=[("Text File",'*.txt')], defaultextension="txt")
        if rule_name:
            rule_file = open(rule_name, "w")
            rule_content = self.root.rule_text.get("1.0", tk.END)
            rule_file.write(rule_content)
            rule_file.close()
            messagebox.showinfo("Info", message="The current rules have been saved.")

    def result_save(self):
        result_name = asksaveasfilename(title="Save Result", initialdir=self.root.result_dir, filetypes=[("Text File", '*.txt')], defaultextension="txt")
        if result_name:
            result_file = open(result_name, "w")
            result_content = self.root.result_text.get("1.0", tk.END)
            result_file.write(result_content)
            result_file.close()
            messagebox.showinfo("Info", message="The current rules have been saved.")

    def help_about(self):
        messagebox.showinfo("About", "Author: Kunyan Han \nVersion 1.1")


if __name__ == '__main__':
    # 实例化Application
    app = Application()

    # 添加菜单
    app.addmenu(MyMenu)

    # 主消息循环
    app.mainloop()



