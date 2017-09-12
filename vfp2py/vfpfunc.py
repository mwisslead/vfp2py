from __future__ import print_function, division

import builtins
import datetime as dt
import os
import sys
import types
import ctypes
import ctypes.util
import traceback
import re
import inspect

import pyodbc

import dateutil.relativedelta

from PySide import QtGui, QtCore

from vfpdatabase import DatabaseContext

SET_PROPS = {
    'bell': ['ON', ''],
    'century': ['OFF', 19, 67, 2029],
    'compatible': ['OFF', 'PROMPT'],
    'cursor': ['ON'],
    'deleted': ['OFF'],
    'exact': ['OFF'],
    'index': [''],
    'multilocks': ['OFF'],
    'near': ['OFF'],
    'notify': ['ON', 'ON'],
    'refresh': [0, 5],
    'status': ['OFF'],
    'status bar': ['ON'],
    'unique': ['OFF'],
}

HOME = sys.argv[0]
if not HOME:
    HOME = sys.executable
HOME = os.path.dirname(os.path.abspath(HOME))

SEARCH_PATH = [HOME]

QTGUICLASSES = [c[1] for c in inspect.getmembers(QtGui, inspect.isclass)]

FONTDICT = {
    'times new roman': 'Times',
}

def _in_qtgui(cls):
    if cls in QTGUICLASSES:
        return True
    return any(_in_qtgui(c) for c in inspect.getmro(cls) if c is not cls)

class HasColor(object):
    @property
    def backcolor(self):
        return widget.palette().color(QtGui.QPalette.Background)

    @backcolor.setter
    def backcolor(self, color):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)

class HasFont(object):
    @property
    def fontname(self):
        try:
            return next(key for key in FONTDICT if self.font().family() == FONTDICT[key])
        except:
            return 'Don\'t know'

    @fontname.setter
    def fontname(self, val):
        try:
            font = self.font()
            font.setFamily(FONTDICT[val.lower()])
            self.setFont(font)
        except:
            pass

    @property
    def fontbold(self):
        return self.font().bold()

    @fontbold.setter
    def fontbold(self, val):
        font = self.font()
        font.setBold(val)
        self.setFont(font)

class Custom(object):
    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.init(*args)

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def init(self, *args, **kwargs):
        pass

    def add_object(self, name, obj):
        setattr(self, name, obj)
        obj.name = name
        obj.parent = self
        if _in_qtgui(type(obj)):
            self.addWidget(obj)

    @property
    def parentform(self):
        try:
            t = self
            while not isinstance(t, Form):
                t = t.parent
            return t
        except:
            raise Exception('object is not a member of a form')

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(type(self), self).__init__()
        self.mdiarea = QtGui.QMdiArea()
        self.mdiarea.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding);
        self.setCentralWidget(self.mdiarea)

    def add_object(self, obj):
        self.mdiarea.addSubWindow(obj)

    @property
    def caption(self):
        return self.windowTitle()

    @caption.setter
    def caption(self, val):
        self.setWindowTitle(val)

    @property
    def height(self):
        return QtGui.QMdainWindow.height(self)

    @height.setter
    def height(self, val):
        self.setFixedHeight(val)

class Form(QtGui.QMdiSubWindow, Custom, HasFont):
    def __init__(self, *args, **kwargs):
        QtGui.QMdiSubWindow.__init__(self)
        self._centralwidget = QtGui.QWidget(self)
        self._vbox = QtGui.QVBoxLayout()
        self._centralwidget.setLayout(self._vbox)
        self.setWidget(self._centralwidget)
        Custom.__init__(self, *args, **kwargs)

    def addWidget(self, obj):
        self._vbox.addWidget(obj)

    @property
    def caption(self):
        return self.windowTitle()

    @caption.setter
    def caption(self, val):
        self.setWindowTitle(val)

    @property
    def height(self):
        return QtGui.QMdiSubWindow.height(self)

    @height.setter
    def height(self, val):
        self.setFixedHeight(val)

class Commandbutton(QtGui.QPushButton, Custom, HasFont):
    def __init__(self, *args, **kwargs):
        QtGui.QPushButton.__init__(self)
        Custom.__init__(self, *args, **kwargs)
        self.clicked.connect(self.click)

    def click(self):
        self.click()

    @property
    def caption(self):
        return self.text()

    @caption.setter
    def caption(self, val):
        self.setText(val)

    @property
    def height(self):
        return QtGui.QPushButton.height(self)

    @height.setter
    def height(self, val):
        self.setFixedHeight(val)

class Label(QtGui.QLabel, Custom, HasFont):
    def __init__(self, *args, **kwargs):
        QtGui.QLabel.__init__(self)
        Custom.__init__(self, *args, **kwargs)

    @property
    def caption(self):
        return self.text()

    @caption.setter
    def caption(self, val):
        self.setText(val)

    @property
    def height(self):
        return QtGui.QLabel.height(self)

    @height.setter
    def height(self, val):
        self.setFixedHeight(val)

class Textbox(QtGui.QLineEdit, Custom, HasColor, HasFont):
    def __init__(self, *args, **kwargs):
        QtGui.QLineEdit.__init__(self)
        Custom.__init__(self, *args, **kwargs)

    @property
    def height(self):
        return QtGui.QLabel.height(self)

    @height.setter
    def height(self, val):
        self.setFixedHeight(val)

    @property
    def value(self):
        return self.text()

    @value.setter
    def value(self, val):
        self.setText(val)

class Checkbox(QtGui.QCheckBox, Custom, HasFont):
    def __init__(self, *args, **kwargs):
        QtGui.QCheckBox.__init__(self)
        Custom.__init__(self, *args, **kwargs)

    @property
    def caption(self):
        return self.text()

    @caption.setter
    def caption(self, val):
        self.setText(val)

    @property
    def height(self):
        return QtGui.QLabel.height(self)

    @height.setter
    def height(self, val):
        self.setFixedHeight(val)

class Combobox(QtGui.QComboBox, Custom, HasFont):
    def __init__(self, *args, **kwargs):
        QtGui.QComboBox.__init__(self)
        Custom.__init__(self, *args, **kwargs)

    def additem(self, val):
        self.addItem(val)

    @property
    def caption(self):
        return self.text()

    @caption.setter
    def caption(self, val):
        self.setText(val)

    @property
    def height(self):
        return QtGui.QLabel.height(self)

    @height.setter
    def height(self, val):
        self.setFixedHeight(val)

class Spinner(Custom):
    pass

class Shape(Custom):
    pass

class Separator(Custom):
    pass

class Toolbar(Custom):
    pass

class Listbox(Custom):
    pass

class Optiongroup(Custom):
    pass

class Optionbutton(Custom):
    pass

class Pageframe(Custom):
    pass

class Page(Custom):
    pass

class Array(object):
    def __init__(self, dim1, dim2=0, offset=0):
        self.columns = bool(dim2)
        self.offset = offset
        if not dim2:
            dim2 = 1
        self.dim1 = int(dim1)
        self.data = [False]*self.dim1*int(dim2)


    def _subarray(self, inds):
        def modify_slice(ind):
            def modify_slice_ind(slice_ind):
                return slice_ind - 1 if slice_ind is not None else None
            return slice(modify_slice_ind(ind.start), modify_slice_ind(ind.stop), ind.step)

        ind = modify_slice(inds)
        data = self.data[ind]
        new_array = Array(len(data), 1, ind.start)
        new_array.data = data
        return new_array

    def _get_index(self, inds):
        if not isinstance(inds, tuple):
            inds = (inds, 1)
        if len(inds) < 2:
            inds = (inds[0], 1)
        ind1, ind2 = [int(ind) - 1 for ind in inds]
        ind = (len(self) // self.dim1)*ind1 + ind2 - self.offset
        if ind < 0:
            raise IndexError('invalid indices')
        return ind

    def __getitem__(self, inds):
        if isinstance(inds, slice):
            return self._subarray(inds)
        return self.data[self._get_index(inds)]

    def __setitem__(self, inds, val):
        self.data[self._get_index(inds)] = val

    def __call__(self, *args):
        return self[args]

    def __len__(self):
        return len(self.data)

    def alen(self, arr_attr=0):
        if arr_attr == 2 and not self.columns:
            return 0
        return {
            0: len(self),
            1: self.dim1,
            2: len(self) // self.dim1,
        }[arr_attr]

    def index(self, val):
        try:
            return self.data.index(val) + 1 + self.offset
        except ValueError:
            return 0

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        dims = (self.dim1,) if self.dim1 == len(self) else (self.dim1, len(self) // self.dim1)
        return '{}({})'.format(type(self).__name__, ', '.join(str(dim) for dim in dims))

class _Variable(object):
    def __init__(self, db):
        self.public_scopes = []
        self.local_scopes = []

        self.db = db

    def _get_scope(self, key):
        if len(self.local_scopes) > 0 and key in self.local_scopes[-1]:
            return self.local_scopes[-1]
        for scope in reversed(self.public_scopes):
            if key in scope:
                return scope

    def __contains__(self, key):
        try:
            self[key]
            return True
        except:
            return False

    def __getitem__(self, key):
        scope = self._get_scope(key)
        if scope is not None:
            return scope[key]
        table_info = self.db._get_table_info()
        if table_info is not None and key in table_info.table.field_names:
            return table_info.table.current_record[key]
        else:
            raise NameError('name {} is not defined'.format(key))

    def __setitem__(self, key, val):
        scope = self._get_scope(key)
        if scope is None:
            scope = self.local_scopes[-1]
        scope[key] = val

    def __delitem__(self, key):
        scope = self._get_scope(key)
        del scope[key]

    def add_private(self, *keys):
        for key in keys:
            self.public_scopes[-1][key] = False

    def add_public(self, *keys, **kwargs):
        for key in keys:
            self.public_scopes[0][key] = kwargs.get('{}_init_val'.format(key), False)

    def pushscope(self):
        self.public_scopes.append({})
        self.local_scopes.append({})

    def popscope(self):
        self.public_scopes.pop()
        self.local_scopes.pop()

    def release(self, mode='Normal', skeleton=None):
        if mode == 'Extended':
            pass
        elif mode == 'Like':
            pass
        elif mode == 'Except':
            pass
        else:
            var_names = []
            for var in self.local_scopes[-1]:
                var_names.append(var)
            for var in self.public_scopes[-1]:
                var_names.append(var)
            for var in var_names:
                del self[var]

    def current_scope(self):
        scope = {}
        for public_scope in self.public_scopes:
            scope.update(public_scope)
        scope.update(self.local_scopes[-1])
        return scope

class _Function(object):
    def __init__(self):
        self.functions = {}

    def __getitem__(self, key):
        if key in self.functions:
            return self.functions[key]['func']
        for scope in variable.public_scopes:
            if key in scope and isinstance(scope[key], Array):
                return scope[key]
        raise Exception('{} is not a procedure'.format(key))

    def __setitem__(self, key, val):
        self.functions[key] = {'func': val, 'source': None}

    def __repr__(self):
        return repr(self.functions)

    def pop(self, key):
        return self.functions.pop(key)

    def set_procedure(self, *procedures, **kwargs):
        for procedure in procedures:
            module = __import__(procedure)
            for obj_name in dir(module):
                obj = getattr(module, obj_name)
                if isinstance(obj, types.FunctionType):
                    self.functions[obj_name] = {'func': obj, 'source': procedure}

    def release_procedure(self, *procedures, **kwargs):
        release_keys = []
        for key in self.functions:
            if self.functions[key]['source'] in procedures:
                release_keys.append(key)
        for key in release_keys:
            self.functions.pop(key)

    def dll_declare(self, dllname, funcname, alias):
        # need something here to determine more about the dll file.
        try:
            dll = ctypes.CDLL(dllname)
        except:
            dll = ctypes.CDLL(ctypes.util.find_library(dllname))
        func = getattr(dll, funcname)
        alias = alias or funcname
        self.functions[alias] = {'func': func, 'source': dllname}

def atline(search, string):
    found = string.find(search)
    if found == -1:
        return 0
    return string[:found].count('\r') + 1

def capslock(on=None):
    pass

def cdx(index, workarea):
    pass

def chrtran(expr, fchrs, rchrs):
     return ''.join(rchrs[fchrs.index(c)] if c in fchrs else c for c in expr)

def ctod(string):
    return dt.datetime.strptime(string, '%m/%d/%Y').date()

def ddeinitiate(a, b):
    pass

def ddesetoption(a, b):
    pass

def ddeterminate(a):
    pass

def ddesetservice(a, b, c=False):
    pass

def ddesettopic(a, b, c):
    pass

def delete_file(string, recycle=False):
    pass

def dow_fix(weekday, firstday=0):
    return (weekday + 2 - (firstday or 1)) % 7 + 1

def error(txt):
    raise Exception(txt)

def fdate(filename, datetype=0):
    if datetype not in (0, 1):
        raise ValueError('datetype is invalid')
    mod_date = dt.datetime.fromtimestamp(os.path.getmtime(filename))
    return mod_date if datetype else mod_date.date()

def ftime(filename):
    return fdate(filename, 1).time()

def filetostr(filename):
    with open(filename) as fid:
        return fid.read().decode('ISO-8859-1')

def _getwords(string, delim=None):
    return [w for w in string.split(delim) if w]

def getwordcount(string, delim=None):
    return len(_getwords(string, delim))

def getwordnum(string, index, delim=None):
    str_list = _getwords(string, delim)
    if 0 <= index <= len(str_list):
        return str_list[index-1]
    return ''

def gomonth(dateval, delta):
    return dateval + dateutil.relativedelta.relativedelta(months=delta)

def home(location=0):
    if location != 0:
        raise Exception('not implemented')
    return HOME

def inkey(seconds=0, hide_cursor=False):
    pass

def isblank(expr):
    try:
        return not expr.strip()
    except:
        return expr is None

def like(matchstr, string):
    matchstr = matchstr.replace('.', r'\.').replace('*', '.*').replace('?', '.')
    return bool(re.match(matchstr, string))

def lineno(flag=None):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    return exc_tb.tb_lineno

def locfile(filename, ext='', caption=''):
    '''find file on path'''
    if os.path.isfile(filename):
        return os.path.abspath(filename)
    dirname = os.path.dirname(filename)
    filename = os.path.basename(filename)
    for path in SEARCH_PATH:
        testpath = os.path.join(path, filename)
        if os.path.isfile(testpath):
            return os.path.abspath(testpath)
    #open dialog to find file
    raise Exception('file not found')

def message(flag=None):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    if flag is None:
        return exc_obj.message
    return traceback.extract_tb(exc_tb)[0][3]

def messagebox(msg, arg1=None, arg2=None, timeout=None, details=''):
    OK_ONLY = 0
    OK_CANCEL = 1
    ABORT_RETRY_IGNORE = 2
    YES_NO_CANCEL = 3
    YES_NO = 4
    RETRY_CANCEL = 5

    NOICON = 0
    STOPSIGN = 16
    QUESTION = 32
    EXCLAMATION = 48
    INFORMATION = 64

    FIRSTBUTTON = 0
    SECONDBUTTON = 256
    THIRDBUTTON = 512

    OK = QtGui.QMessageBox.Ok
    CANCEL = QtGui.QMessageBox.Cancel
    ABORT = QtGui.QMessageBox.Abort
    RETRY = QtGui.QMessageBox.Retry
    IGNORE = QtGui.QMessageBox.Ignore
    YES = QtGui.QMessageBox.Yes
    NO = QtGui.QMessageBox.No

    RETURN_OK = 1
    RETURN_CANCEL = 2
    RETURN_ABORT = 3
    RETURN_RETRY = 4
    RETURN_IGNORE = 5
    RETURN_YES = 6
    RETURN_NO = 7

    def center_widget(widget):
        '''center the widget on the screen'''
        widget_pos = widget.frameGeometry()
        screen_center = QtGui.QDesktopWidget().screenGeometry().center()
        widget_pos.moveCenter(screen_center)
        widget.move(widget_pos.topLeft())

    '''mimics MESSAGEBOX function from visual foxpro'''
    flags=0
    title='pyvfp'
    if arg1 is not None:
        if isinstance(arg1, str):
            title = arg1
            if arg2 is not None:
                flags = arg2
        else:
            flags = arg1
            if arg2 is not None:
                title = arg2
    flags = int(flags) & 1023

    buttons = {OK_ONLY: ((OK,), OK),
               OK_CANCEL: ((OK, CANCEL), CANCEL),
               ABORT_RETRY_IGNORE: ((ABORT, RETRY, IGNORE), IGNORE),
               YES_NO_CANCEL: ((YES, NO, CANCEL), CANCEL),
               YES_NO: ((YES, NO), NO),
               RETRY_CANCEL: ((RETRY, CANCEL), CANCEL)
              }[flags & 15]
    buttonobj = buttons[0][0]
    for button in buttons[0][1:]:
        buttonobj |= button

    icon = {NOICON: QtGui.QMessageBox.NoIcon,
            STOPSIGN: QtGui.QMessageBox.Critical,
            QUESTION: QtGui.QMessageBox.Question,
            EXCLAMATION: QtGui.QMessageBox.Warning,
            INFORMATION: QtGui.QMessageBox.Information
           }[flags & (15 << 4)]

    default_button = min(len(buttons[0])-1, (flags >> 8))

    msg_box = QtGui.QMessageBox(icon, title, msg, buttons=buttonobj)
    msg_box.setDefaultButton(buttons[0][default_button])
    msg_box.setEscapeButton(buttons[1])
    if details:
        msg_box.setDetailedText(details)

    msg_box.show()

    retval = [0]
    def closebox():
        t = retval
        t[0] = -1
        msg_box.close()

    if timeout:
        QtCore.QTimer().singleShot(float(timeout)*1000, closebox)
    button = msg_box.exec_()
    retval = retval[0]
    center_widget(msg_box)
    return {OK: RETURN_OK,
            CANCEL: RETURN_CANCEL,
            ABORT: RETURN_ABORT,
            RETRY: RETURN_RETRY,
            IGNORE: RETURN_IGNORE,
            YES: RETURN_YES,
            NO: RETURN_NO
           }[button] if retval != -1 else -1

def num_to_str(num, length=10, decimals=0):
    length = int(length)
    decimals = int(decimals)
    if num == int(num):
        string = str(int(num))
        if length >= len(string):
            return ' ' * (length-len(string)) + string
        return '*' * length
    else:
        string = '{:f}'.format(num)
        integer, mantissa = string.split('.')
        if decimals:
            if len(mantissa) <= decimals:
                mantissa += '0' * (decimals - len(mantissa))
            else:
                if int(mantissa[decimals:]) > 0:
                    mantissa = str(int(mantissa[:decimals]) + 1)
                    if len(mantissa) > decimals:
                        integer += 1
                        mantissa = '0' * decimals
                mantissa = mantissa[:decimals]
            string = integer + '.' + mantissa
        else:
            string = integer
        if length >= len(string):
            return ' ' * (length-len(string)) + string
        else:
            string = '{:e}'.format(num)
            if length >= len(string):
                return ' ' * (length-len(string)) + string
            string, exp = string.split('e')
            exp = 'e' + exp
            if length <= len(exp):
                return '*' * length
            return string[:length-len(exp)] + exp

def program(level=None):
    trace = traceback.extract_stack()[:-1]
    if level is None:
        level = -1
    elif level < 0:
        return len(trace) - 1
    elif level == 0:
        level = 1
    if level >= len(trace):
        return ''
    prg = trace[level][2]
    if prg == '_program_main':
        prg = re.sub(r'.py$', '', trace[level][0])
    return prg.upper()

def quarter(datetime, start_month=1):
    if not datetime:
        return 0
    month = (datetime.month - start_month) % 12
    return (month - (month % 3)) // 3 + 1

def quit(message=None, flags=None, title=None):
    sys.exit()

def ratline(search, string):
    found = string.rfind(search)
    if found == -1:
        return 0
    return string[:found].count('\r') + 1

def rgb(red, green, blue):
    return QtGui.QColor(red, green, blue)

def seconds():
    now = dt.datetime.now()
    return (now - dt.datetime.combine(now, dt.time(0, 0))).seconds

def strextract(string, begin, end='', occurance=1, flag=0):
    begin = re.escape(begin)
    end = re.escape(end)
    if end:
        between = '.*?'
    else:
        between = '.*'
    if flag & 4:
        regstr = '({}{}{})'.format(begin, between, end)
    else:
        regstr = '{}({}){}'.format(begin, between, end)
    try:
        if flag & 1:
            flags = re.IGNORECASE
        else:
            flags = 0
        return re.findall(regstr, string, flags=flags)[occurance - 1]
    except:
        if flag & 2 and end:
            return strextract(string, begin, '', occurance, flag & 5)
        return ''

def strtofile(string, filename, flag=0):
    flag = int(flag)
    if flag not in (0, 1, 2, 4):
        raise ValueError('invalid flag')

    mode = 'ab' if flag == 1 else 'wb'

    with open(filename, mode) as fid:
        if flag == 2:
            fid.write(string.encode('utf-16'))
        elif flag == 4:
            fid.write(b'\xef\xbb\xbf')
            fid.write(string.encode('utf-8'))
        else:
            fid.write(string)

def strtran(string, old, new='', start=0, maxreplace=None, flags=0):
    retstr = ''
    while start > 0:
        try:
            ind = string.find(old) + len(old)
            retstr += string[:ind]
            string = string[ind:]
        except:
            break
        start -= 1
    if maxreplace:
        retstr += string.replace(old, new, maxreplace)
    else:
        retstr += string.replace(old, new)
    return retstr

def stuff(string, start, num_replaced, repl):
    return string[:start-1] + repl + string[start-1+num_replaced:]

def sqlcommit(conn):
    try:
        conn.commit()
        return 1
    except:
        return -1

def sqlconnect(name, userid=None, password=None, shared=False):
    return pyodbc.connect('dsn=' + name)

def sqlstringconnect(*args):
    if len(args) == 0 or len(args) == 1 and isinstance(args[0], bool):
        connect_string = None #should pop up a dialog
        shared = args[0] if args else False
    else:
        connect_string = args[0]
        shared = args[1] if len(args) > 1 else False
    return pyodbc.connect(connect_string)

def _odbc_cursor_to_db(results, cursor_name):
    if not cursor_name:
        cursor_name = 'sqlresult'
    try:
        values = results.fetchall()
        if not values:
            raise Exception('')
        column_info = values[0].cursor_description
        columns = []
        for i, column in enumerate(column_info):
            field_name = column[0][:10]
            field_type = {
                int: 'N',
                str: 'C',
                bool: 'L',
                float: 'N',
            }[column[1]]
            if field_type == 'N':
                field_lens = column[4:6]
            elif field_type == 'L':
                field_lens = ''
            else:
                field_lens = '({})'.format(column[4])
            columns.append('{} {}{}'.format(field_name, field_type, field_lens))
        db.use(None, db.select_function(cursor_name), None)
        db.create_table(cursor_name + '.dbf', columns, 'free')
        for value in values:
            db.insert(cursor_name, tuple(value))
        db.goto(cursor_name, 0)
    except:
        pass

def sqlexec(conn, cmd='', cursor_name='', count_info=''):
    try:
        results = conn.execute(cmd)
        _odbc_cursor_to_db(results, cursor_name)
        return 1
    except:
        return -1

def sqlrollback(conn):
    try:
        conn.rollback()
        return 1
    except:
        return -1


def sqltables(conn, table_type='', cursor_name=''):
    try:
        _odbc_cursor_to_db(conn.cursor().tables(), cursor_name)
        return 1
    except:
        return -1

def sqldisconnect(connection):
    connection.close()

def vfp_sys(funcnum, *args):
    if funcnum == 16:
        import imp
        if hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__"):
            return os.path.dirname(sys.executable)
        return os.path.dirname(sys.argv[0])

def version(ver_type=4):
    if ver_type == 5:
        return 900

def wait(msg, to=None, window=[-1, -1], nowait=False, noclear=False, timeout=-1):
    pass

def set(setword, *args, **kwargs):
    setword = setword.lower()
    settings = SET_PROPS[setword]
    if not kwargs.get('set_value', False):
        return settings[args[0]] if args else settings[0]
    if setword == 'bell':
        if args[0].lower() not in ('to', 'on', 'off'):
            raise ValueError('Bad argument: {}'.format(args[0]))
        if args[0] == 'TO':
            settings[1] = '' if len(args) == 1 else args[1]
        else:
            settings[0] = args[0].upper()
    elif setword == 'century':
        if len(args) > 0:
            settings[0] = args[0]
        if 'century' in kwargs:
            settings[1] = kwargs['century']
        if 'rollover' in kwargs:
            settings[2] = kwargs['rollover']
    elif setword == 'compatible':
        if args[0].lower() not in ('on', 'off'):
            raise ValueError('Bad argument: {}'.format(args[0]))
        settings[0] = args[0].upper()
        if len(args) > 1:
            if args[1].lower() not in ('prompt', 'noprompt'):
                settings[1] = args[1].upper()
    elif setword == 'notify':
        if 'cursor' in kwargs:
            settings[1] = kwargs['cursor']
        else:
            settings[0] = args[0]
    elif setword in ('cursor', 'deleted', 'exact', 'multilocks', 'near', 'status', 'status bar', 'unique'):
        if args[0].lower() not in ('on', 'off'):
            raise ValueError('Bad argument: {}'.format(args[0]))
        settings[0] = args[0].upper()
    elif setword in ('index', 'refresh'):
        settings = args
    SET_PROPS[setword] = settings

def create_object(objtype, *args):
    pass

def clearall():
    pass

def _exec():
    variable['_vfp'].show()
    return qt_app.exec_()

db = DatabaseContext()
variable = _Variable(db)
function = _Function()
error_func = None
variable.pushscope()
qt_app = QtGui.QApplication(())
variable.add_public('_vfp')
variable['_vfp'] = MainWindow()
variable['_vfp'].caption = 'VFP To Python'
