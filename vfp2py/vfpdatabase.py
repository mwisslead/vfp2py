# coding=utf-8
from __future__ import absolute_import, division, print_function

import os
import inspect

from argparse import Namespace

import dbf


class DatabaseWorkspace(object):
    def __init__(self, tablename, alias=None):
        self.name = (alias or '').lower()
        self.table = dbf.Table(tablename)
        self.table.open(dbf.READ_WRITE)
        if len(self.table) > 0:
            self.table.goto(0)
        self.locate = None
        self.found = False
        self.seek = None
        self.index = {}
        self.current_index = None

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
                return self.get_workarea(tablename) + 1
        except:
            return 0

    def _get_table_info(self, tablename=None):
        return self.open_tables[self.get_workarea(tablename)]

    @property
    def _current_record(self):
        return self._get_table_info().table.current_record

    def _current_record_copy(self):
        record = Namespace()
        table = self._get_table_info().table
        for field in table.field_names:
            setattr(record, field, table.current_record[field])
        return record

    def _update_from(self, val):
        record = self._current_record
        if not record:
            return
        fields = dbf.source_table(record).field_names
        update = {field: getattr(val, field) for field in fields if hasattr(val, field)}
        if not update:
            try:
                update = {field: v for field, v in zip(fields, val)}
            except:
                return
        dbf.write(record, **update)

    def create_table(self, tablename, setup_string, free):
        if free == 'free':
            dbf.Table(tablename, setup_string)
            self.use(tablename, 0, 'shared')

    def alter_table(self, tablename, alter_type, field_specs):
        if alter_type == 'add':
            self._get_table_info(tablename).table.add_fields(field_specs)
        else:
            self._get_table_info(tablename).table.delete_fields(field_specs)

    def select(self, tablename):
        self.current_table = self.get_workarea(tablename)

    def use(self, tablename, workarea, opentype, alias=None):
        if tablename is None:
            if workarea is 0:
                return
            self.open_tables[self.get_workarea(workarea) - 1] = None
            return
        if self.used(tablename):
            raise Exception('File is in use.')
        if workarea == 0:
            workarea = self.open_tables.index(None)
        self.open_tables[workarea] = DatabaseWorkspace(tablename, alias)

    def alias(self, tablename=None):
        table_info = self._get_table_info(tablename)
        return table_info.name or os.path.splitext(os.path.basename(table_info.table.filename))[0]

    def dbf(self, tablename=None):
        try:
            return self._get_table_info(tablename).table.filename
        except:
            pass

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

    def replace(self, tablename, scope, field, value):
        if not tablename:
            field = field.lower().rsplit('.', 1)
            tablename = field[0] if len(field) == 2 else None
            field = field[-1]
        for record in self._get_records(tablename, scope):
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
            if not isinstance(values, (tuple, dict)):
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
        num = num - 1 if num > 0 else num
        table.goto(num)

    def _get_records(self, tablename, scope, for_cond=None, while_cond=None):
        def reset(used_table, saved_current):
            if saved_current < 0:
                used_table.top()
            elif saved_current == len(used_table):
                used_table.bottom()
            else:
                used_table.goto(saved_current)
        save_current_table = self.current_table
        self.select(tablename)
        table = self._get_table_info().table
        if not table:
            self.current_table = save_current_table
            return
        save_current = table.current
        if scope[0].lower() == 'all':
            table.goto(0)
        if scope[0].lower() == 'record':
            table.goto(scope[1] - 1)
            condition = lambda table: table.current == scope[1] - 1
        elif scope[0].lower() == 'next':
            final_record = table.current + scope[1]
            condition = lambda table: table.current < final_record
        else:
            condition = lambda table: bool(table.current_record)
        if not for_cond:
            for_cond = lambda: True
        if not while_cond:
            while_cond = lambda: True
        if not table.current_record:
            self.current_table = save_current_table
            return
        while condition(table) and while_cond():
            if for_cond():
                yield table.current_record
            try:
                table.skip(1)
            except:
                break
        if scope[0].lower() in ('all', 'rest'):
            table.bottom()
        elif scope[0].lower() == 'next':
            reset(table, save_current + scope[1] - 1)
        elif scope[0].lower() == 'record':
            reset(table, scope[1] - 1)
        self.current_table = save_current_table

    def scanner(self, condition=None, scope=('rest',)):
        if not condition:
            condition = lambda: True
        workspace = self.current_table
        record = self.recno()
        t = self._get_table_info(workspace).table
        if scope[0] == 'all':
            self.goto(workspace, 0)
        if len(t) > 0 and condition():
            yield
        while not self.eof(workspace):
            self.skip(workspace, 1)
            if not condition():
                continue
            yield
        self.goto(workspace, record)

    def count(self, tablename, scope, **kwargs):
        return len(list(self._get_records(tablename, scope, **kwargs)))

    def copy_structure(self, tablename):
        dbf.Table(tablename, self._get_table_info().table.structure())

    def delete_record(self, tablename, scope, recall=False, **kwargs):
        for record in self._get_records(tablename, scope, **kwargs):
            (dbf.undelete if recall else dbf.delete)(record)

    def sum(self, tablename, scope, sumexpr, **kwargs):
        return sum(sumexpr() for record in self._get_records(tablename, scope, **kwargs))

    def pack(self, pack, tablename, workarea):
        if tablename:
            table = dbf.Table(tablename)
            table.open(dbf.READ_WRITE)
            table.pack()
            table.close()
        else:
            self._get_table_info(workarea).table.pack()

    def reindex(self, compact_flag):
        self._get_table_info().table.reindex()

    def index_on(self, field, indexname, order, tag_flag, compact_flag, unique_flag):
        table_info = self._get_table_info()
        table_info.index[indexname] = table_info.table.create_index(lambda rec, field=field: getattr(rec, field))
        table_info.current_index = indexname

    def close_tables(self, all_flag):
        self.open_tables = [None] * 32767

    def recno(self):
        try:
            return dbf.recno(self.open_tables[self.current_table].table.current_record) + 1
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

    def locate(self, tablename=None, for_cond=None, while_cond=None, nooptimize=None):
        kwargs = locals()
        kwargs = {key: kwargs[key] for key in ('for_cond', 'while_cond') if kwargs[key] is not None}
        self._get_table_info(tablename).locate = (record for record in list(self._get_records(tablename, ('rest',), **kwargs)))
        self.continue_locate(tablename)

    def continue_locate(self, tablename=None):
        workarea = self._get_table_info(tablename)
        if not (workarea and workarea.locate):
            return
        try:
            record = next(workarea.locate)
            dbf.source_table(record).goto(dbf.recno(record))
            workarea.found = True
        except StopIteration:
            workarea.table.bottom()
            workarea.locate = None
            workarea.found = False

    def seek(self, tablename, key_expr, key_index=None, key_index_file=None, descending=False):
        table_info = self._get_table_info(tablename)
        if not(table_info.seek and not key_index):
            table_info.seek = (record for record in table_info.index[table_info.current_index].search((key_expr,)))
        try:
            record = next(table_info.seek)
        except StopIteration:
            table_info.table.bottom()
            table_info.found = False
            return
        dbf.source_table(record).goto(dbf.recno(record))
        table_info.found = True

    def found(self, tablename=None):
        workarea = self._get_table_info(tablename)
        return workarea.found if workarea else False

    def browse(self):
        table_info = self._get_table_info()
        table = table_info.table
        print('Tablename:', table_info.name)
        print(table.field_names)
        for record in table:
            print('->' if record is table.current_record else '  ', record[:])

    def zap(self, tablename):
        self._get_table_info().table.zap()

    def field(self, field_item, tablename=None, flag=0):
        try:
            return self._get_table_info(tablename).table.field_names[field_item - 1]
        except:
            return 0

    def afields(self):
        pass

    def fcount(self, tablename=None):
        try:
            return self._get_table_info().table.field_count
        except:
            return 0

    def cpdbf(self, tablename=None):
        try:
            return self._get_table_info(tablename).table.codepage.code
        except AttributeError:
            return 0
