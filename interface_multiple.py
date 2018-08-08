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

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

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
        self.headcombobox = ttk.Combobox(topframe, values=["Empty"], textvariable=self.head_keyvar, state="disabled")
        headbutton = tk.Button(topframe, text="Add Head", command=self.__add_head)


        # -- 放置位置
        glabel.place(x=0, y=5)
        gentry.place(x=80, y=5)
        gbutton.place(x=250, y=0)
        headlabel.place(x=290, y=5)
        self.headcombobox.place(x=335, y=5)
        headbutton.place(x=510, y=0)

        # -- 绑定事件
        gentry.bind('<Return>', func=self.__refresh)



        # 中部rule区域
        rulelabel = tk.Label(ruleframe, text="Please input the judge rules")
        ruletext_frame = tk.Frame(ruleframe) # 放rule_text和rule_rightbar, rule_bottombar
        rule_rightbar = tk.Scrollbar(ruletext_frame, orient=tk.VERTICAL)
        rule_bottombar = tk.Scrollbar(ruletext_frame, orient=tk.HORIZONTAL)
        self.rule_text = tk.Text(ruletext_frame, width=80, height=10, yscrollcommand=rule_rightbar.set, xscrollcommand=rule_bottombar.set, wrap="none") # 设置滚动条 - 不换行
        # font = {"宋体"，12, "normal"}
        clearbutton= tk.Button(ruleframe, text="  Clear  ", command=self.__clear_rule)
        rulebutton = tk.Button(ruleframe, text="Analyze", command=self.__analyze)

        # -- 放置位置
        rule_rightbar.pack(side=tk.RIGHT, fill=tk.Y)
        rule_bottombar.pack(side=tk.BOTTOM, fill=tk.X)
        self.rule_text.pack(side=tk.LEFT, fill=tk.BOTH)

        rulelabel.place(x=0, y=0)
        ruletext_frame.place(x=0, y=20)

        clearbutton.place(x=440, y=int(ruletext_frame.place_info()['y'])+165-5)
        rulebutton.place(x=510, y=int(ruletext_frame.place_info()['y'])+165-5)

        rule_rightbar.config(command=self.rule_text.yview)
        rule_bottombar.config(command=self.rule_text.xview)
        self.rule_text.bind('<Button-3>', func=self.__popup)


        # 结果区域
        result_label = tk.Label(resultframe, text="Analysis Result")
        resulttext_frame = tk.Frame(resultframe) # 放rule_text和rule_rightbar
        result_rightbar = tk.Scrollbar(resulttext_frame, orient=tk.VERTICAL)
        result_bottombar = tk.Scrollbar(resulttext_frame, orient=tk.HORIZONTAL)
        self.result_text = tk.Text(resulttext_frame, width=80, height=25, yscrollcommand=result_rightbar.set, xscrollcommand=result_bottombar.set, wrap="none")
        deletebutton = tk.Button(resultframe, text="Delete Result", command=self.__clear_result)
        self.switchbutton = tk.Button(resultframe, text="Switch Result", command=self.switch_result, state="disabled")

        # -- 放置位置
        result_rightbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_bottombar.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH)

        result_label.place(x=0, y=0)
        resulttext_frame.place(x=0, y=20)
        deletebutton.place(x=400, y=380)
        self.switchbutton.place(x=490, y=380)

        # -- 设置命令
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
        self.filename = filedialog.askopenfilename(title="Open File", initialdir=self.root.csv_dir, filetypes=[('CSV File','*.csv'),('All Files','*')])
        self.entryvar.set(self.filename.split('/')[-1])

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
            #try:
                print (self.filename)
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

            #except:
            #    messagebox.showerror("Warning", message = "The judging rule seems to have some error, please revise it and try again.")


    def __add_head(self):
        head = self.headcombobox.get()
        if head=="Title in CSV":
            messagebox.showwarning("Warning", message="No head is chosen!")
        else:
            self.rule_text.insert(tk.END, head+" ")

    def __clear_rule(self):
        self.rule_text.delete("1.0", tk.END)

    def __clear_result(self):
        self.result_text.delete("1.0", tk.END)

    def switch_result(self):
        if self.result_type=="row":
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, self.result_rule_str+"\n")
            self.result_type = "rule"
        else:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, self.result_row_str + "\n")
            self.result_type = "row"





class Multi(tk.Frame):
    '''第二页'''
    def __init__(self, parent, root):
        super().__init__(parent)
        self.createWidgets()
        self.root = root
        self.result_type = "row"
        self.filename_list = [None]*3



    def createWidgets(self):
        topframe = tk.Frame(self, width=580, height=120)
        topframe.pack(side=tk.TOP)
        ruleframe = tk.Frame(self, width=580, height=230) # 由于元素使用pack这里必须设定width和height 否则frame不会显示
        ruleframe.pack(side=tk.TOP)
        resultframe = tk.Frame(self, width=580, height=350)
        resultframe.pack(side=tk.TOP)

        # 顶部区域
        # 第一个读取文件
        glabel1 = tk.Label(topframe, text="Target file1:")
        self.entryvar1 = tk.StringVar()
        gentry1 = tk.Entry(topframe, textvariable=self.entryvar1, width=25)
        gbutton1 = tk.Button(topframe, command=lambda: self.__openfile(1), text='...')
        headlabel1 = tk.Label(topframe, text="Head")
        self.head_keyvar1 = tk.StringVar()
        self.head_keyvar1.set("Title in CSV")
        self.headcombobox1 = ttk.Combobox(topframe, values=["Empty"], textvariable=self.head_keyvar1, state="disabled")
        headbutton1 = tk.Button(topframe, text="Add Head", command=lambda: self.__add_head(1))

        glabel1.place(x=0, y=5)
        gentry1.place(x=80, y=5)
        gbutton1.place(x=250, y=0)
        headlabel1.place(x=290, y=5)
        self.headcombobox1.place(x=335, y=5)
        headbutton1.place(x=510, y=0)


        # 第二个读取文件
        glabel2 = tk.Label(topframe, text="Target file2:")
        self.entryvar2 = tk.StringVar()
        gentry2 = tk.Entry(topframe, textvariable=self.entryvar2, width=25)
        gbutton2 = tk.Button(topframe, command=lambda: self.__openfile(2), text = '...')
        headlabel2 = tk.Label(topframe, text="Head")
        self.head_keyvar2 = tk.StringVar()
        self.head_keyvar2.set("Title in CSV")
        self.headcombobox2 = ttk.Combobox(topframe, values=["Empty"], textvariable=self.head_keyvar2, state="disabled")
        headbutton2 = tk.Button(topframe, text="Add Head", command=lambda: self.__add_head(2))

        glabel2.place(x=0, y=40)
        gentry2.place(x=80, y=40)
        gbutton2.place(x=250, y=40-5)
        headlabel2.place(x=290, y=40)
        self.headcombobox2.place(x=335, y=40)
        headbutton2.place(x=510, y=40-5)


        # 第三个读取文件
        glabel3 = tk.Label(topframe, text="Target file3:")
        self.entryvar3 = tk.StringVar()
        gentry3 = tk.Entry(topframe, textvariable=self.entryvar3, width=25)
        gbutton3 = tk.Button(topframe, command=lambda: self.__openfile(3), text = '...')
        headlabel3 = tk.Label(topframe, text="Head")
        self.head_keyvar3 = tk.StringVar()
        self.head_keyvar3.set("Title in CSV")
        self.headcombobox3 = ttk.Combobox(topframe, values=["Empty"], textvariable=self.head_keyvar3, state="disabled")
        headbutton3 = tk.Button(topframe, text="Add Head", command=lambda: self.__add_head(3))

        glabel3.place(x=0, y=75)
        gentry3.place(x=80, y=75)
        gbutton3.place(x=250, y=75-5)
        headlabel3.place(x=290, y=75)
        self.headcombobox3.place(x=335, y=75)
        headbutton3.place(x=510, y=75-5)



        # 中部rule区域
        rulelabel = tk.Label(ruleframe, text="Please input the judge rules")
        ruletext_frame = tk.Frame(ruleframe) # 放rule_text和rule_rightbar, rule_bottombar
        rule_rightbar = tk.Scrollbar(ruletext_frame, orient=tk.VERTICAL)
        rule_bottombar = tk.Scrollbar(ruletext_frame, orient=tk.HORIZONTAL)
        self.rule_text = tk.Text(ruletext_frame, width=80, height=10, yscrollcommand=rule_rightbar.set, xscrollcommand=rule_bottombar.set, wrap="none") # 设置滚动条 - 不换行
        # font = {"宋体"，12, "normal"}
        clearbutton= tk.Button(ruleframe, text="  Clear  ", command=self.__clear_rule)
        rulebutton = tk.Button(ruleframe, text="Analyze", command=self.__analyze)

        # -- 放置位置
        rule_rightbar.pack(side=tk.RIGHT, fill=tk.Y)
        rule_bottombar.pack(side=tk.BOTTOM, fill=tk.X)
        self.rule_text.pack(side=tk.LEFT, fill=tk.BOTH)

        rulelabel.place(x=0, y=0)
        ruletext_frame.place(x=0, y=20)

        clearbutton.place(x=440, y=int(ruletext_frame.place_info()['y'])+165-5)
        rulebutton.place(x=510, y=int(ruletext_frame.place_info()['y'])+165-5)

        rule_rightbar.config(command=self.rule_text.yview)
        rule_bottombar.config(command=self.rule_text.xview)
        self.rule_text.bind('<Button-3>', func=self.__popup)


        # 结果区域
        result_label = tk.Label(resultframe, text="Analysis Result")
        resulttext_frame = tk.Frame(resultframe) # 放rule_text和rule_rightbar
        result_rightbar = tk.Scrollbar(resulttext_frame, orient=tk.VERTICAL)
        result_bottombar = tk.Scrollbar(resulttext_frame, orient=tk.HORIZONTAL)
        self.result_text = tk.Text(resulttext_frame, width=80, height=20, yscrollcommand=result_rightbar.set, xscrollcommand=result_bottombar.set, wrap="none")
        deletebutton = tk.Button(resultframe, text="Delete Result", command=self.__clear_result)
        self.switchbutton = tk.Button(resultframe, text="Switch Result", command=self.switch_result, state="disabled")

        # -- 放置位置
        result_rightbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_bottombar.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH)

        result_label.place(x=0, y=0)
        resulttext_frame.place(x=0, y=20)
        deletebutton.place(x=400, y=310) #440 310
        self.switchbutton.place(x=490, y=310) #510,310

        # -- 设置命令
        result_rightbar.config(command=self.result_text.yview)
        result_bottombar.config(command=self.result_text.xview)


        edit_items = ['Cut', 'Copy', 'Paste', 'Delete']
        self.Rbtnmenubar = tk.Menu(self, tearoff=0)
        self.Rbtnmenubar.add_command(label=edit_items[0], command=self.__cut_clk)
        self.Rbtnmenubar.add_command(label=edit_items[1], command=self.__copy_clk)
        self.Rbtnmenubar.add_command(label=edit_items[2], command=self.__paste_clk)
        self.Rbtnmenubar.add_command(label=edit_items[3], command=self.__delete_clk)

    def __popup(self, event):  # 右键弹出
        self.Rbtnmenubar.post(event.x_root, event.y_root)

    def __cut_clk(self):  # 剪切右键的回调
        try:
            setText(self.rule_text.get(SEL_FIRST, SEL_LAST))
            self.rule_text.delete(SEL_FIRST, SEL_LAST)
        except:
            pass

    def __copy_clk(self):  # 复制右键的回调
        try:
            setText(self.rule_text.get(SEL_FIRST, SEL_LAST))
        except:
            pass

    def __paste_clk(self):  # 粘贴右键的回调
        self.rule_text.insert(INSERT, getText())

    def __delete_clk(self):  # 剪切右键的回调
        try:
            self.rule_text.delete(SEL_FIRST, SEL_LAST)
        except:
            pass



    def __openfile(self, i):
        self.filename = filedialog.askopenfilename(title="Open File", initialdir=self.root.csv_dir, filetypes=[('CSV File','*.csv'),('All Files','*')])
        eval("self.entryvar"+str(i)).set(self.filename.split('/')[-1])

        if not self.filename:
            pass
        else:
            try:
                col_type = readCsv(self.filename)["col_type"]
                eval("self.head_keyvar"+str(i)).set("Title in CSV")
                eval("self.headcombobox"+str(i))["values"] = list(col_type.keys()) # modify the combobox after csv is read
                eval("self.headcombobox"+str(i))["state"] = "normal"
                #self.result_text.delete('1.0', tk.END) # multi就不用删了
                self.result_text.insert(tk.END, "Loaded " + self.filename + "\n\n")
                self.filename_list[i-1] = self.filename
            except:
                messagebox.showerror("Error", message="The file cannot be opened, please try again.")

    def __refresh(self, i):
        self.filename = eval("self.entryvar"+str(i)).get()
        # self.textbox.insert(tk.END, self.filename+"\r\n")
        # self.textbox.update()

    def __analyze(self):
        self.rule = self.rule_text.get('1.0', tk.END)
        if self.rule=='\n':
            messagebox.showwarning("Warning", message="Please Input the Judge Rules!")
        else:
            #try:
                #print (self.filename)
                a = Expr_multi(self.rule, self.filename_list)
                file_involved = a.judge()
                print (file_involved)
                err_row_dict = a.err_row_dict
                err_rule_dict = a.err_rule_dict

                # 分析结果 以row为顺序
                self.result_row_str = "Current File: \n"
                for num in file_involved:
                    self.result_row_str = self.result_row_str + self.filename_list[num-1] + '\n'
                self.result_row_str = self.result_row_str + '\n\n'
                self.result_rule_str = self.result_row_str

                if len(err_row_dict)==0:
                    self.result_row_str = self.result_row_str + "No Error!\n"
                else:
                    for row, row_list in err_row_dict.items():
                        self.result_row_str = self.result_row_str + "Error Line:" + str(row+2) + "\n" # 对应csv中行号
                        for err_rule in row_list:
                            self.result_row_str = self.result_row_str + "Error Rule:" + err_rule + "\n"
                        self.result_row_str = self.result_row_str + "\n"



                # 分析结果 以rule为顺序
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

            #except:
            #    messagebox.showerror("Warning", message = "The judging rule seems to have some error, please revise it and try again.")


    def __add_head(self, i):
        head = eval("self.headcombobox"+str(i)).get()
        if head=="Title in CSV":
            messagebox.showwarning("Warning", message="No head is chosen!")
        else:
            self.rule_text.insert(tk.END, head+" ")

    def __clear_rule(self):
        self.rule_text.delete("1.0", tk.END)

    def __clear_result(self):
        self.result_text.delete("1.0", tk.END)

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
        self.frame_name = root.curframe_name
        self.frame = root.curframe_name

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

        # 创建“Mode”下拉菜单
        switchmenu = tk.Menu(self.menubar, tearoff=0)
        self.userChoice = IntVar()
        if root.curframe_name==Single: #默认选中
            self.userChoice.set(1)
        elif root.curframe_name==Multi:
            self.userChoice.set(2)
        switchmenu.add_radiobutton(label="单文件模式", variable=self.userChoice, value=1, command=lambda: root.show_frame(Single))
        switchmenu.add_radiobutton(label="多文件模式", variable=self.userChoice, value=2, command=lambda: root.show_frame(Multi))

        # 创建“Help”下拉菜单
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.help_about)

        # 将前面两个菜单加到菜单栏
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.menubar.add_cascade(label="Mode", menu=switchmenu)
        self.menubar.add_cascade(label="Help", menu=helpmenu)

        # 最后再将菜单栏整个加到窗口 root
        root.config(menu=self.menubar)


    def file_open(self):
        self.root.filename = filedialog.askopenfilename(title="Open File", initialdir=self.root.csv_dir, filetypes=[('CSV File', '*.csv'), ('All Files', '*')])
        if self.frame_name==Single:
            self.frame.entryvar.set(self.frame.framename.split('/')[-1])

            try:
                col_type = readCsv(self.frame.filename)["col_type"]
                self.frame.head_keyvar.set("Title in CSV")
                self.frame.headcombobox["values"] = list(col_type.keys())  # modify the combobox after csv is read
                self.frame.headcombobox["state"] = "normal"
                self.frame.result_text.delete('1.0', tk.END)
                self.frame.result_text.insert(tk.END, "Loaded " + self.frame.filename + "\n\n")
            except:
                messagebox.showerror("Error", message="The file cannot be opened, please try again.")

        elif self.frame_name==Multi:
            is_set = 0
            for i in range(3):
                if not eval("self.frame.entryvar"+str(i+1)).get():
                    eval("self.frame.entryvar"+str(i+1)).set(self.frame.filename.split('/')[-1])
                    is_set = i+1
                    break
            if not is_set:
                self.frame.entryvar1.set(self.frame.filename.split('/')[-1])
                is_set = 1

            if not self.frame.filename:
                pass
            else:
                try:
                    col_type = readCsv(self.frame.filename)["col_type"]
                    eval("self.frame.head_keyvar"+str(is_set)).set("Title in CSV")
                    eval("self.frame.headcombobox"+str(is_set))["values"] = list(col_type.keys())  # modify the combobox after csv is read
                    eval("self.frame.headcombobox"+str(is_set))["state"] = "normal"
                    #self.frame.result_text.delete('1.0', tk.END)
                    self.frame.result_text.insert(tk.END, "Loaded " + self.frame.filename + "\n\n")
                    self.frame.filename_list[is_set-1] = self.frame.filename
                except:
                    messagebox.showerror("Error", message="The file cannot be opened, please try again.")


    def rule_open(self):
        rule_name = askopenfilename(title="Open Rule", initialdir=self.root.rule_dir, filetypes=[("Text File",'*.txt')])
        if rule_name:
            rule_file = open(rule_name, "r")
            rule_content = rule_file.read()
            rule_file.close()
            self.frame.rule_text.delete("1.0", tk.END)
            self.frame.rule_text.insert("1.0", rule_content)

    def rule_save(self):
        rule_name = asksaveasfilename(title="Save Rule", initialdir=self.root.rule_dir, filetypes=[("Text File",'*.txt')], defaultextension="txt")
        if rule_name:
            rule_file = open(rule_name, "w")
            rule_content = self.frame.rule_text.get("1.0", tk.END)
            rule_file.write(rule_content)
            rule_file.close()
            messagebox.showinfo("Info", message="The current rules have been saved.")

    def result_save(self):
        result_name = asksaveasfilename(title="Save Result", initialdir=self.root.result_dir, filetypes=[("Text File", '*.txt')], defaultextension="txt")
        if result_name:
            result_file = open(result_name, "w")
            result_content = self.frame.result_text.get("1.0", tk.END)
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



