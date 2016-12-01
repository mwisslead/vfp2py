import builtins
import datetime
import os

import dbf

SCOPES = []

class Form(object):
    def __init__(self):
        pass

def pushscope():
    global SCOPES
    SCOPES.append({})

def popscope():
    global SCOPES
    SCOPES.pop()

def alltrim(string):
    return string.strip()

def delete_file(string, recycle=False):
    pass

def error(txt):
    raise Exception(txt)

def file(string):
     return os.path.isfile(string.lower())

def messagebox(message, flags, title):
    pass

def quit(message, flags, title):
    pass

def isblank(expr):
    return not not expr

def release(varname, publics=False, skeleton=None, like=True):
    if varname:
        pass #pop the variable from locals
    else:
        pass #pop all variables locals
    if publics:
        pass #pop all public variables
        
    
def chr(num):
    return __builtin__.chr(int(num))

def chrtran(expr, fchrs, rchrs):
     return ''.join(rchrs[fchrs.index(c)] if c in fchrs else c for c in expr)

def ctod(string):
    return datetime.datetime.strptime(string, '%m/%d/%Y').date()

def space(num):
    return ' ' * int(num)

def dtoc(dateval):
    return dateval.strftime('%m/%d/%Y')

def rgb(red, green, blue):
    return (red, green, blue)

def wait(msg, to=None, window=[-1, -1], nowait=False, noclear=False, timeout=-1):
    pass

def select(tablename):
    pass

def set(setitem, *args, **kwargs):
    pass

class Database_Context(object):
    def __init__(self):
        self.current_table = -1
        self.open_tables = [{'name': None}]*10

    def create_table(self, tablename, setup_string, free):
        if free == 'free':
            dbf.Table(tablename, setup_string)

    def select(self, tablename):
        if isinstance(tablename, (int, float)):
            self.current_table = int(tablename)
            return
        tablenames = [t['name'] for t in self.open_tables]
        if tablename in tablenames:
            self.current_table = tablenames.index(tablename)
        else:
            raise Exception('Table is not currently open')

    def use(self, tablename, workarea, opentype):
        tablenames = [t['name'] for t in self.open_tables]
        if tablename is None and workarea is None:
            table = self.open_tables[self.current_table]['table']
            table.close()
            self.open_tables[self.current_table] = {'name': None}
            self.current_table = -1
            return
        elif tablename is None:
            ind = self.tablenames.index(workarea)
            table = self.open_tables[ind]['table']
            table.close()
            self.open_tables[ind] = {'name': None}
            if ind == self.current_table:
                self.current_table = -1
            return
        table = dbf.Table(tablename)
        table.open()
        if workarea == 0:
            workarea = tablenames.index(None)
        self.open_tables[workarea] = {'name': tablename, 'table': table}

db = Database_Context()
