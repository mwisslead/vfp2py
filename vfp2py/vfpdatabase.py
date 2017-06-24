import dbf

class DatabaseContext(object):
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
            self.use(tablename, 0, 'shared')

    def select(self, tablename):
        self.current_table = self._table_index(tablename)
        table_data = self.open_tables[self.current_table]
        if table_data['recno'] == 0:
            table_data['recno'] = min(len(table_data['table']), 1)

    def use(self, tablename, workarea, opentype):
        if tablename is None:
            if workarea is 0:
                return
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

    def used(self, tablename):
        try:
            table = self._get_table(tablename)
            return True
        except:
            return False

    def append(self, tablename, editwindow):
        table_info = self._get_table_info(tablename)
        table = table_info['table']
        table.append()
        table_info['recno'] = len(table)

    def append_from(self, tablename, from_source, from_type='dbf'):
        table = self._get_table(tablename)
        if from_type == 'dbf':
            from_table = dbf.Table(from_source)
            from_table.open()
            for record in from_table:
                table.append(record)
            from_table.close()

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
        table_info = self._get_table_info(table)
        table = table_info['table']
        recno = table_info['recno']
        record = table[recno-1]
        dbf.write(record, **{field: value})

    def insert(self, tablename, values):
        table_info = self._get_table_info(tablename)
        table = table_info['table']
        if isinstance(values, Array):
            for i in range(1,values.alen(1)+1):
                table.append(tuple(values[i, j] for j in range(1,values.alen(2)+1)))
        else:
            if isinstance(values, Custom):
                values = {field: getattr(values, field) for field in table.field_names if hasattr(values, field)}
            elif values is None:
                local = inspect.stack()[1][0].f_locals
                scope = variable.current_scope()
                values = {field: scope[field] for field in table.field_names if field in scope}
                values.update({field: local[field] for field in table.field_names if field in local})
            table.append(values)
        table_info['recno'] = len(table)

    def skip(self, tablename, skipnum):
        table_info = self._get_table_info(tablename)
        table_info['recno'] += int(skipnum)

    def goto(self, tablename, num):
        table_info = self._get_table_info(tablename)
        if num == -1:
            num = len(table_info['table']) - 1
        table_info['recno'] = num + 1

    def delete_record(self, tablename, scope, num, for_cond=None, while_cond=None, recall=False):
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
        else:
            records = table[recno-1:recno-1+num]
        for record in records:
            if not while_cond():
                break
            if for_cond():
                if recall:
                    dbf.delete(record)
                else:
                    dbf.undelete(record)
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

    def index_on(self, field, indexname, order, tag_flag, compact_flag, unique_flag):
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

    def recsize(self, workarea=None):
        table = self._get_table(workarea)
        return table.record_length

    def bof(self, workarea=None):
        table_info = self._get_table_info(workarea)
        return table_info['recno'] == 0

    def eof(self, workarea=None):
        table_info = self._get_table_info(workarea)
        return table_info['recno'] == len(table_info['table'])

    def deleted(self, workarea=None):
        table_info = self._get_table_info(workarea)
        dbf.is_deleted(table_info['table'][table_info['recno']])

    def browse(self):
        table_info = self._get_table_info()
        table = table_info['table']
        print('Tablename:', table_info['name'])
        print(table.field_names)
        for i, record in enumerate(table):
            if table_info['recno'] == i+1:
                print('->', record[:])
            else:
                print(record[:])
