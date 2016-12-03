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

class _Database_Context(object):
    def __init__(self):
        self.current_table = -1
        self.open_tables = [{'name': None}]*10

    def _table_index(self, tablename=None):
        if not tablename:
            ind = self.current_table
        elif isinstance(tablename, (int, float)):
            ind = tablename
        else:
            tablenames = [t['name'] for t in self.open_tables]
            if tablename in tablenames:
                ind = tablenames.index(tablename)
            else:
                raise Exception('Table is not currently open')
        return ind

    def _get_table_info(self, tablename=None):
        return self.open_tables[self._table_index(tablename)]

    def _get_table(self, tablename=None):
        return self._get_table_info(tablename)['table']

    def create_table(self, tablename, setup_string, free):
        if free == 'free':
            dbf.Table(tablename, setup_string)

    def select(self, tablename):
        self.current_table = self._table_index(tablename)
        table_data = self.open_tables[self.current_table]
        if table_data['recno'] == 0:
            table_data['recno'] = min(len(table_data['table']), 1)

    def use(self, tablename, workarea, opentype):
        if tablename is None:
            table = self.open_tables[self._table_index(workarea)]['table']
            table.close()
            self.open_tables[self.current_table] = {'name': None}
            self.current_table = -1
            return
        table = dbf.Table(tablename)
        table.open()
        if workarea == 0:
            tablenames = [t['name'] for t in self.open_tables]
            workarea = tablenames.index(None)
        self.open_tables[workarea] = {'name': tablename, 'table': table, 'recno': 0}
        self.current_table = workarea

    def append(self, tablename, editwindow):
        table_info = self._get_table_info(tablename)
        table = table_info['table']
        table.append()
        table_info['recno'] = len(table)

    def replace(self, tablename, fieldname, value, scope):
        table_info = self._get_table_info(tablename)
        table = table_info['table']
        recno = table_info['recno']
        record = table[recno-1]
        dbf.write(record, **{fieldname: value})

    def skip(self, tablename, skipnum):
        table_info = self._get_table_info(tablename)
        table_info['recno'] += int(skipnum)

    def delete_record(self, tablename, scope, num, for_cond=None, while_cond=None):
        save_current_table = self.current_table
        if not for_cond:
            for_cond = lambda: True
        if not while_cond:
            while_cond = lambda: True
        self.select(tablename)
        table_info = self._get_table_info()
        table = table_info['table']
        recno = table_info['recno']
        reccount = len(table)
        if scope.lower() == 'rest':
            records = table[recno-1:reccount]
        for record in records:
            if not while_cond():
                break
            if for_cond():
                dbf.delete(record)
        self.current_table = save_current_table

    def recno(self):
        try:
            return self.open_tables[self.current_table]['recno']
        except:
            return 0

    def reccount(self):
        try:
            return len(self.open_tables[self.current_table]['table'])
        except:
            return 0

class _Variable(object):
    def __init__(self, db):
        self.variables = {}
        self.db = db

    def __getitem__(self, key):
        if key in self.variables:
            return self.variables[key]
        elif key in self.db._get_table().field_names:
            table_info = self.db._get_table_info()
            return table_info['table'][table_info['recno']][key]

    def __setitem__(self, key, val):
        self.variables[key] = val

db = _Database_Context()
variable = _Variable(db)

recno = db.recno
reccount = db.reccount
