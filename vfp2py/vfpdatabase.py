from __future__ import print_function

import os
import inspect

import dbf


class DatabaseWorkspace(object):
    def __init__(self, tablename, alias=None):
        self.name = (alias or '').lower()
        self.table = dbf.Table(tablename)
        self.table.open()
        if len(self.table) > 0:
            self.table.goto(0)

    def _is_alias(self, alias):
        alias = alias.lower()
        filename = self.table.filename.lower()
        possible_aliases = (
            self.name,
            filename,
            os.path.splitext(filename)[0],
            os.path.basename(filename),
            os.path.basename(os.path.splitext(filename)[0]),
        )
        return alias in possible_aliases

class DatabaseContext(object):
    def __init__(self):
        self.close_tables(None)
        self.current_table = 0

    def get_workarea(self, tablename=None):
        if not tablename:
            ind = self.current_table
        elif isinstance(tablename, (int, float)):
            ind = tablename
        else:
            try:
                ind = next(idx for idx, open_table in enumerate(self.open_tables) if open_table and open_table._is_alias(tablename))
            except StopIteration:
                raise Exception('Table is not currently open')
        return ind

    def select_function(self, tablename):
        try:
            if isinstance(tablename, float):
                tablename = int(tablename)
            if isinstance(tablename, int):
                if tablename == 0:
                    return self.current_table + 1
                elif tablename == 1:
                    return next(len(self.open_tables) - i for i, table in enumerate(reversed(self.open_tables)) if table is None)
                else:
                    return tablename if self.open_tables[tablename - 1] else 0
            if not tablename:
                return next(i+1 for i, table in enumerate(self.open_tables) if table is None)
            else:
                return self.get_workspace(tablename) + 1
        except:
            return 0

    def _get_table_info(self, tablename=None):
        return self.open_tables[self.get_workarea(tablename)]

    def create_table(self, tablename, setup_string, free):
        if free == 'free':
            dbf.Table(tablename, setup_string)
            self.use(tablename, 0, 'shared')

    def select(self, tablename):
        self.current_table = self.get_workarea(tablename)

    def use(self, tablename, workarea, opentype):
        if tablename is None:
            if workarea is 0:
                return
            self.open_tables[self.get_workarea(workarea) - 1] = None
            return
        if workarea == 0:
            workarea = self.open_tables.index(None)
        self.open_tables[workarea] = DatabaseWorkspace(tablename)

    def used(self, tablename):
        try:
            self.get_workarea(tablename)
            return True
        except:
            return False

    def append(self, tablename, editwindow):
        table_info = self._get_table_info(tablename)
        table_info.table.append()
        self.goto(tablename, -1)

    def append_from(self, tablename, from_source, from_type='dbf'):
        table = self._get_table_info(tablename).table
        if from_type == 'dbf':
            with dbf.Table(from_source) as from_table:
                for record in from_table:
                    table.append(record)

    def replace(self, field, value, scope):
        field = field.lower().split('.')
        if len(field) > 1:
            if len(field) == 2:
                table = str(field[0])
            else:
                table = '.'.join(field[:-1])
            field = field[-1]
        else:
            field = field[0]
            table = None
        record = self._get_table_info(table).current_record
        dbf.write(record, **{field: value})

    def insert(self, tablename, values):
        table_info = self._get_table_info(tablename)
        table = table_info.table
        if values is None:
            local = inspect.stack()[1][0].f_locals
            scope = variable.current_scope()
            values = {field: scope[field] for field in table.field_names if field in scope}
            values.update({field: local[field] for field in table.field_names if field in local})
        try:
            for i in range(1,values.alen(1)+1):
                table.append(tuple(values[i, j] for j in range(1,values.alen(2)+1)))
        except AttributeError:
            if not isinstance(values, dict):
                values = {field: getattr(values, field) for field in table.field_names if hasattr(values, field)}
            table.append(values)
        self.goto(tablename, -1)

    def skip(self, tablename, skipnum):
        try:
            self._get_table_info(tablename).table.skip(skipnum)
        except dbf.Eof:
            pass

    def goto(self, tablename, num):
        table = self._get_table_info(tablename).table
        if num == -1:
            table.bottom()
        else:
            num = num - 1
            table.goto(num)

    def _get_records(self, tablename, scope, for_cond, while_cond):
        save_current_table = self.current_table
        self.select(tablename)
        if not for_cond:
            for_cond = lambda: True
        if not while_cond:
            while_cond = lambda: True
        table = self._get_table_info().table
        if scope.lower() == 'rest':
            condition = lambda table: not table.eof
        else:
            recno = self.recno()
            condition = lambda table: not table.eof and dbf.recno(table.current_record) - recno < num
        records = []
        while condition(table) and while_cond():
            if for_cond():
                records.append(table.current_record)
            self.skip(None, 1)
        self.current_table = save_current_table

    def delete_record(self, tablename, scope, num, for_cond=None, while_cond=None, recall=False):
        for record in self._get_records(tablename, scope, for_cond, while_cond):
            (dbf.undelete if recall else dbf.delete)(record)

    def pack(self, pack, tablename, workarea):
        if tablename:
            table = dbf.Table(tablename)
            table.open()
            table.pack()
            table.close()
        else:
            self._get_table_info(workarea).table.pack()

    def reindex(self, compact_flag):
        self._get_table_info().table.reindex()

    def index_on(self, field, indexname, order, tag_flag, compact_flag, unique_flag):
        pass

    def close_tables(self, all_flag):
        self.open_tables = [None] * 32767

    def recno(self):
        try:
            return dbf.recno(self.open_tables[self.current_table].table.current_record)
        except:
            return 0

    def reccount(self):
        try:
            return len(self.open_tables[self.current_table].table)
        except:
            return 0

    def recsize(self, workarea=None):
        return self._get_table_info(workarea).table.record_length

    def bof(self, workarea=None):
        return self._get_table_info(workarea).table.bof

    def eof(self, workarea=None):
        return self._get_table_info(workarea).table.eof

    def deleted(self, workarea=None):
        return dbf.is_deleted(self._get_table_info(workarea).table.current_record)

    def browse(self):
        table_info = self._get_table_info()
        table = table_info.table
        print('Tablename:', table_info.name)
        print(table.field_names)
        for record in table:
            print('->' if record is table.current_record else '  ', record[:])
