# -*- coding:utf-8 -*-

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
            return self.items[len(self.items) - 1]
    def size(self):
        return len(self.items)


class judge:
    def __init__(self,expression):
        self.expression = expression
