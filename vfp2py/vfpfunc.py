import builtins
import datetime
import os

import dbf

PUBLIC_SCOPE = {}
PRIVATE_SCOPES = []
LOCAL_SCOPES = []

class Form(object):
    def __init__(self):
        pass

class Array(object):
    def __init__(self, dim1, dim2=1):
        self.dim1 = dim1
        self.data = [False]*int(dim1*dim2)

    def _get_index(self, inds):
        if not isinstance(inds, tuple):
            inds = (inds, 1)
        dim1, dim2 = inds
        ind = self.dim1*(dim2-1) + dim1 - 1
        if ind < 0:
            raise IndexError('invalid indices')
        return int(ind)

    def __getitem__(self, inds):
        return self.data[self._get_index(inds)]

    def __setitem__(self, inds, val):
        self.data[self._get_index(inds)] = val

    def __call__(self, *args):
        return self[args]

def pushscope():
    global PRIVATE_SCOPES, LOCAL_SCOPES
    PRIVATE_SCOPES.append({})
    LOCAL_SCOPES.append({})

def popscope():
    global PRIVATE_SCOPES, LOCAL_SCOPES
    PRIVATE_SCOPES.pop()
    LOCAL_SCOPES.pop()

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

def do_command(command, module, *args, **kwargs):
    mod = __import__(module)
    cmd = getattr(mod, command)
    cmd(*args, **kwargs)

def call_if_callable(expr):
    if callable(expr):
        return expr()
    return expr

def create_object(objtype, *args):
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
            table_info['recno'] += 1
        table_info['recno'] = recno
        self.current_table = save_current_table

    def pack(self, pack, tablename, workarea):
        if tablename:
            table = dbf.Table(tablename)
            table.open()
            table.pack()
            table.close()
        else:
            table = self._get_table(workarea)
            table.pack()

    def reindex(self, compact_flag):
        table = self._get_table()
        table.reindex()

    def index_on(field, indexname, order, tag_flag, compact_flag, unique_flag):
        pass

    def close_tables(self, all_flag):
        for i, table in enumerate(self.open_tables):
            if table['name'] is not None:
                self.use(None, i, None)

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
        self.db = db

    def _get_scope(self, key):
        if len(LOCAL_SCOPES) > 0 and key in LOCAL_SCOPES[-1]:
            return LOCAL_SCOPES[-1]
        for scope in reversed(PRIVATE_SCOPES):
            if key in scope:
                return scope
        if key in PUBLIC_SCOPE:
            return PUBLIC_SCOPE

    def __getitem__(self, key):
        scope = self._get_scope(key)
        table_info = self.db._get_table_info()
        if scope is not None:
            return scope[key]
        elif table_info['name'] is not None and key in table_info['table'].field_names:
            return table_info['table'][table_info['recno']-1][key]
        else:
            raise NameError('name {} is not defined'.format(key))

    def __setitem__(self, key, val):
        scope = self._get_scope(key)
        if scope is None:
            scope = LOCAL_SCOPES[-1]
        scope[key] = val

    def add_private(self, key):
        PRIVATE_SCOPES[-1][key] = None

class _Function(object):
    def __init__(self):
        self.functions = {}

    def __getitem__(self, key):
        if key in self.functions:
            return self.functions[key]
        for scope in PRIVATE_SCOPES:
            if key in scope and isinstance(scope[key], Array):
                return scope[key]
        if key in PUBLIC_SCOPE and isinstance(scope[key], Array):
            return PUBLIC_SCOPE[key]
        raise Exception('{} is not a procedure'.format(key))

    def __setitem__(self, key, val):
        self.functions[key] = val

    def set_procedure(self, procedure_name, additive=False):
        pass


db = _Database_Context()
variable = _Variable(db)
function = _Function()

recno = db.recno
reccount = db.reccount

def array(arrayname, dim1, dim2=1, public=False):
    arr = Array(dim1, dim2)
    if public:
        PUBLIC_SCOPE[arrayname] = arr
    else:
        PRIVATE_SCOPES[-1][arrayname] = arr
