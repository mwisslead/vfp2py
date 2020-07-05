# coding=utf-8
from __future__ import absolute_import, division, print_function

import datetime as dt
import os
import sys
import types
import ctypes
import ctypes.util
import traceback
import re
import inspect
import glob
import importlib
import functools

import pyodbc

import dateutil.relativedelta

try:
    import win32com.client
except ImportError:
    pass

from .vfpdatabase import DatabaseContext

SET_PROPS = {
    'bell': ['ON', ''],
    'century': ['OFF', 19, 67, 2029],
    'compatible': ['OFF', 'PROMPT'],
    'cursor': ['ON'],
    'deleted': ['OFF'],
    'escape': ['OFF'],
    'exact': ['OFF'],
    'index': [''],
    'multilocks': ['OFF'],
    'near': ['OFF'],
    'notify': ['ON', 'ON'],
    'procedure': None,
    'refresh': [0, 5],
    'status': ['OFF'],
    'status bar': ['ON'],
    'talk': ['ON'],
    'unique': ['OFF'],
}

HOME = sys.argv[0]
if not HOME:
    HOME = sys.executable
HOME = os.path.dirname(os.path.abspath(HOME))

SEARCH_PATH = [HOME]

PCOUNTS = []

_str = str
try:
    from PySide import QtGui, QtCore

    QTGUICLASSES = [c[1] for c in inspect.getmembers(QtGui, inspect.isclass)]

    def _in_qtgui(cls):
        if cls in QTGUICLASSES:
            return True
        return any(_in_qtgui(c) for c in inspect.getmro(cls) if c is not cls)

    class HasColor(object):
        @property
        def backcolor(self):
            return self.palette().color(QtGui.QPalette.Background)

        @backcolor.setter
        def backcolor(self, color):
            palette = self.palette()
            palette.setColor(self.backgroundRole(), color)
            self.setPalette(palette)

        @property
        def forecolor(self):
            return self.palette().color(QtGui.QPalette.Foreground)

        @forecolor.setter
        def forecolor(self, color):
            palette = self.palette()
            palette.setColor(self.foregroundRole(), color)
            self.setPalette(palette)

    class HasFont(object):
        @property
        def fontname(self):
            return self.font().family()

        @fontname.setter
        def fontname(self, val):
            font = self.font()
            font.setFamily(val)
            self.setFont(font)

        @property
        def fontbold(self):
            return self.font().bold()

        @fontbold.setter
        def fontbold(self, val):
            font = self.font()
            font.setBold(val)
            self.setFont(font)

        @property
        def fontitalic(self):
            return self.font().italic()

        @fontitalic.setter
        def fontitalic(self, val):
            font = self.font()
            font.setItalic(val)
            self.setFont(font)

        @property
        def fontstrikethru(self):
            return self.font().strikeOut()

        @fontstrikethru.setter
        def fontstrikethru(self, val):
            font = self.font()
            font.setStrikeOut(val)
            self.setFont(font)

        @property
        def fontunderline(self):
            return self.font().fontunderline()

        @fontunderline.setter
        def fontunderline(self, val):
            font = self.font()
            font.setUnderline(val)
            self.setFont(font)

        @property
        def fontsize(self):
            return self.font().pointSize()

        @fontsize.setter
        def fontsize(self, val):
            font = self.font()
            font.setPointSize(val)
            self.setFont(font)

    class Custom(object):
        def __init__(self, *args, **kwargs):
            self._assign()
            for key in kwargs:
                setattr(self, key, kwargs[key])
            if _in_qtgui(type(self)) and 'parent' in kwargs:
                self.parent.add_object(self)
            self.init(*args)

        def init(self, *args, **kwargs):
            pass

        def add_object(self, obj):
            try:
                self.addWidget(obj)
            except:
                pass

        def addobject(self, name, *args):
            name = name.lower()
            setattr(self, name, create_object(*args, name=name, parent=self))

        @property
        def parentform(self):
            try:
                t = self
                while not isinstance(t, (Form, Toolbar)):
                    t = t.parent
                return t
            except:
                raise _EXCEPTION('object is not a member of a form')

        def _assign(self):
            pass

    class MainWindow(QtGui.QMainWindow):
        def __init__(self):
            super(type(self), self).__init__()
            self.mdiarea = QtGui.QMdiArea()
            self.mdiarea.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding);
            self.setCentralWidget(self.mdiarea)

        def add_object(self, obj):
            if isinstance(obj, Toolbar):
                self.addToolBar(obj)
            else:
                self.mdiarea.addSubWindow(obj)

        @property
        def caption(self):
            return self.windowTitle()

        @caption.setter
        def caption(self, val):
            self.setWindowTitle(val)

        @property
        def height(self):
            return QtGui.QMainWindow.height(self)

        @height.setter
        def height(self, val):
            self.setFixedHeight(val)

        @property
        def icon(self):
            return self.windowIcon()

        @icon.setter
        def icon(self, iconfile):
            self.setWindowIcon(QtGui.QIcon(iconfile))

    class Formset(Custom):
        pass

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

        def release(self):
            self.close()

        def destroy(self):
            pass

        def closeEvent(self, event):
            self.destroy()

        @property
        def caption(self):
            return self.windowTitle()

        @caption.setter
        def caption(self, val):
            self.setWindowTitle(val)

        @property
        def height(self):
            return self._centralwidget.height()

        @height.setter
        def height(self, val):
            self._centralwidget.setFixedHeight(val)

        @property
        def width(self):
            return self._centralwidget.width()

        @height.setter
        def width(self, val):
            self._centralwidget.setFixedWidth(val)

        @property
        def icon(self):
            return self.windowIcon()

        @icon.setter
        def icon(self, iconfile):
            self.setWindowIcon(QtGui.QIcon(iconfile))

    class Commandbutton(QtGui.QPushButton, Custom, HasFont):
        def __init__(self, *args, **kwargs):
            QtGui.QPushButton.__init__(self)
            Custom.__init__(self, *args, **kwargs)
            self.clicked.connect(self.click)

        def click(self):
            pass

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

        @property
        def width(self):
            return QtGui.QPushButton.width(self)

        @height.setter
        def width(self, val):
            self.setFixedWidth(val)

        @property
        def enabled(self):
            return self.isEnabled()

        @enabled.setter
        def enabled(self, val):
            self.setEnabled(val)

        @property
        def visible(self):
            return self.isVisible()

        @visible.setter
        def visible(self, val):
            self.setVisible(val)

        @property
        def picture(self):
            return QtGui.QPushButton.icon(self)

        @picture.setter
        def picture(self, iconfile):
            self.setIcon(QtGui.QIcon(iconfile))

        @property
        def tooltiptext(self):
            return self.toolTip()

        @tooltiptext.setter
        def tooltiptext(self, val):
            self.setToolTip(val)

        @property
        def specialeffect(self):
            if self.isFlat():
                return 2
            else:
                return 0

        @specialeffect.setter
        def specialeffect(self, val):
            self.setFlat(val == 2)

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

        @property
        def width(self):
            return QtGui.QLabel.width(self)

        @height.setter
        def width(self, val):
            self.setFixedWidth(val)

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

        @property
        def visible(self):
            return self.isVisible()

        @visible.setter
        def visible(self, val):
            self.setVisible(val)

        def focusInEvent(self, event):
            self.gotfocus()

        def focusOutEvent(self, event):
            self.lostfocus()

        def setfocus(self):
            self.setFocus()

    class Checkbox(QtGui.QCheckBox, Custom, HasFont):
        def __init__(self, *args, **kwargs):
            QtGui.QCheckBox.__init__(self)
            Custom.__init__(self, *args, **kwargs)
            self.clicked.connect(self.click)
            self.clicked.connect(self.interactivechange)

        def click(self):
            pass

        def interactivechange(self):
            pass

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
            self.currentIndexChanged.connect(self.interactivechange)

        def additem(self, val):
            index = self.currentIndex()
            self.blockSignals(True)
            self.addItem(val)
            self.setCurrentIndex(index)
            self.blockSignals(False)

        @property
        def value(self):
            return self.currentText()

        @value.setter
        def value(self, val):
            index = self.findText(val, QtCore.Qt.MatchFixedString)
            self.blockSignals(True)
            self.setCurrentIndex(index)
            self.blockSignals(False)
            self.programmaticchange()

        def programmaticchange(self):
            pass

        def interactivechange(self):
            pass

        @property
        def caption(self):
            return self.text()

        @caption.setter
        def caption(self, val):
            self.setText(val)

        @property
        def height(self):
            return QtGui.QComboBox.height(self)

        @height.setter
        def height(self, val):
            self.setFixedHeight(val)

        @property
        def width(self):
            return QtGui.QComboBox.width(self)

        @height.setter
        def width(self, val):
            self.setFixedWidth(val)

        @property
        def style(self):
            if self.isEditable():
                return 0
            else:
                return 2

        @style.setter
        def style(self, val):
            self.setEditable(val == 0)

    class Spinner(QtGui.QSpinBox, Custom, HasFont, HasColor):
        def __init__(self, *args, **kwargs):
            QtGui.QSpinBox.__init__(self)
            Custom.__init__(self, *args, **kwargs)
            self.pressed = False
            self.installEventFilter(self)
            self.valueChanged.connect(self.interactivechange)

        def eventFilter(self, widget, event):
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                self.pressed = True
            if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
                if self.pressed:
                    self.click()
                self.pressed = False
            return QtGui.QWidget.eventFilter(self, widget, event)

        def click(self):
            pass

        def interactivechange(self):
            pass

        def programmaticchange(self):
            pass

        @property
        def value(self):
            return QtGui.QSpinBox.value(self)

        @value.setter
        def value(self, val):
            self.blockSignals(True)
            self.setValue(val)
            self.blockSignals(False)
            self.programmaticchange()

    class Shape(QtGui.QFrame, Custom):
        def __init__(self, *args, **kwargs):
            QtGui.QFrame.__init__(self)
            Custom.__init__(self, *args, **kwargs)
            self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)

        @property
        def height(self):
            return QtGui.QComboBox.height(self)

        @height.setter
        def height(self, val):
            self.setFixedHeight(val)

        @property
        def width(self):
            return QtGui.QComboBox.width(self)

        @height.setter
        def width(self, val):
            self.setFixedWidth(val)

    class Separator(QtGui.QFrame, Custom):
        def __init__(self, *args, **kwargs):
            QtGui.QFrame.__init__(self)
            Custom.__init__(self, *args, **kwargs)
            self.setFrameStyle(QtGui.QFrame.VLine | QtGui.QFrame.Plain)
            palette = self.palette()
            palette.setColor(self.foregroundRole(), QtGui.QColor(0, 0, 0, 0))
            self.setPalette(palette)
            margin = 4
            self.setContentsMargins(margin, 0, margin, 0)

    class Toolbar(QtGui.QToolBar, Custom):
        def __init__(self, *args, **kwargs):
            QtGui.QToolBar.__init__(self)
            Custom.__init__(self, *args, **kwargs)

    class Listbox(QtGui.QListWidget, Custom):
        def __init__(self, *args, **kwargs):
            QtGui.QListWidget.__init__(self)
            self.multiselect = 0
            Custom.__init__(self, *args, **kwargs)
            self._source = ''

        @property
        def rowsource(self):
            return self._source

        @rowsource.setter
        def rowsource(self, source):
            self._source = source
            table = DB._get_table_info(source).table
            for record in table:
                self.addItem(QtGui.QListWidgetItem(_str(record[0])))

        @property
        def multiselect(self):
            return int(self.selectionMode() == QtGui.QAbstractItemView.MultiSelection)

        @multiselect.setter
        def multiselect(self, mode):
            self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection if mode else QtGui.QAbstractItemView.SingleSelection)

    class Grid(QtGui.QTableWidget, Custom, HasFont):
        def __init__(self, *args, **kwargs):
            QtGui.QTableWidget.__init__(self)
            Custom.__init__(self, *args, **kwargs)
            self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            self._source = ''
            self.cellClicked.connect(self._update_recno)
            self.cellClicked.connect(self.click)
            self.cellDoubleClicked.connect(self.dblclick)

        def _update_recno(self):
            table = DB._get_table_info(self._source).table.goto(self.currentRow())
            self.refresh()

        def click(self):
            pass

        def dblclick(self):
            pass

        def refresh(self):
            table = DB._get_table_info(self._source).table
            labels = table.field_names
            self.setColumnCount(len(labels))
            self.setRowCount(len(table))
            self.setVerticalHeaderLabels(['>' if record is table.current_record else '  ' for record in table])
            self.setHorizontalHeaderLabels(labels)

            for i, record in enumerate(table):
                for j, val in enumerate(record):
                    self.setItem(i, j, QtGui.QTableWidgetItem(_str(val)))

        def focusInEvent(self, event):
            self.refresh()

        @property
        def allowrowsizing(self):
            return self.verticalHeader().resizeMode(0) == QtGui.QHeaderView.Interactive

        @allowrowsizing.setter
        def allowrowsizing(self, val):
            self.verticalHeader().setResizeMode(QtGui.QHeaderView.Interactive if val else QtGui.QHeaderView.Fixed)

        @property
        def recordsource(self):
            return self._source

        @recordsource.setter
        def recordsource(self, source):
            self._source = source
            self.refresh()

        @property
        def allowcellselection(self):
            return self.selectionBehavior() != QtGui.QAbstractItemView.SelectItems

        @allowcellselection.setter
        def allowcellselection(self, mode):
            self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems if mode else QtGui.QAbstractItemView.SelectRows)
            self.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers if mode else QtGui.QAbstractItemView.NoEditTriggers)

    class Optiongroup(QtGui.QWidget, Custom):
        def __init__(self, *args, **kwargs):
            QtGui.QWidget.__init__(self)
            self._group = QtGui.QButtonGroup()
            self._vbox = QtGui.QVBoxLayout()
            self.setLayout(self._vbox)
            Custom.__init__(self, *args, **kwargs)

        def add_object(self, obj):
            self._vbox.addWidget(obj)
            self._group.addButton(obj)

        @property
        def enabled(self):
            return any(button.enabled for button in self._group.buttons())

        @enabled.setter
        def enabled(self, val):
            for button in self._group.buttons():
                button.enabled = val

        @property
        def buttoncount(self):
            return len(self._group.buttons())

        @buttoncount.setter
        def buttoncount(self, val):
            for i in range(val, self.buttoncount):
                self._group.buttons()[-1].deleteLater()
            for i in range(self.buttoncount, val):
                caption = 'option {}'.format(i + 1)
                name = caption.replace(' ', '')
                setattr(self, name, Optionbutton(caption=caption, name=name, parent=self))

    class Optionbutton(QtGui.QRadioButton, Custom, HasFont):
        def __init__(self, *args, **kwargs):
            QtGui.QRadioButton.__init__(self)
            Custom.__init__(self, *args, **kwargs)

        @property
        def caption(self):
            return self.text()

        @caption.setter
        def caption(self, val):
            self.setText(val)

        @property
        def enabled(self):
            return self.isEnabled()

        @enabled.setter
        def enabled(self, val):
            self.setEnabled(val)

    class Pageframe(QtGui.QTabWidget, Custom, HasFont):
        def __init__(self, *args, **kwargs):
            QtGui.QTabWidget.__init__(self)
            Custom.__init__(self, *args, **kwargs)

        def addWidget(self, widget):
            self.addTab(widget, widget.caption)

    class Page(QtGui.QWidget, Custom, HasFont):
        def __init__(self, *args, **kwargs):
            QtGui.QWidget.__init__(self)
            self._vbox = QtGui.QVBoxLayout()
            self.setLayout(self._vbox)
            self.caption = kwargs['name']
            Custom.__init__(self, *args, **kwargs)

        def addWidget(self, widget):
            self._vbox.addWidget(widget)

    class Image(Custom):
        pass

    class Timer(Custom):
        pass

    class Container(Custom):
        pass

    class Editbox(Custom):
        pass

    class Dataenvironment(Custom):
        pass

    qt_app = QtGui.QApplication(())

    def _exec():
        S['_screen'].show()
        return qt_app.exec_()

except ImportError:
    class Custom(object):
        pass

    class MainWindow(Custom):
        pass

    class Formset(Custom):
        pass

    class Form(Custom):
        pass

    class Commandbutton(Custom):
        pass

    class Label(Custom):
        pass

    class Textbox(Custom):
        pass

    class Checkbox(Custom):
        pass

    class Combobox(Custom):
        pass

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

    class Grid(Custom):
        pass

    class Optiongroup(Custom):
        pass

    class Optionbutton(Custom):
        pass

    class Pageframe(Custom):
        pass

    class Page(Custom):
        pass

    class Image(Custom):
        pass

    class Timer(Custom):
        pass

    class Container(Custom):
        pass

    class Editbox(Custom):
        pass

    class Dataenvironment(Custom):
        pass


_EXCEPTION = Exception


class Exception(object):
    def __init__(self):
        self.message = ''
        self.lineno = 0
        self.errorno = 0
        self.procedure = ''
        self.stacklevel = 0
        self.linecontents = ''

    @classmethod
    def from_pyexception(cls, exc):
        trace = traceback.extract_stack()
        obj = cls()
        obj.message = _str(exc)
        if hasattr(exc, '__traceback__'):
            tb = exc.__traceback__
        else:
            tb = sys.exc_info()[2]
        obj.lineno = tb.tb_lineno
        filename = os.path.splitext(os.path.basename(tb.tb_frame.f_code.co_filename))[0]
        obj.procedure = filename + '.' + tb.tb_frame.f_code.co_name
        obj.stacklevel = len(trace) - 1
        return obj

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
        return '{}({})'.format(type(self).__name__, ', '.join(_str(dim) for dim in dims))

class _Memvar(object):
    def __init__(self):
        self.__dict__['public_scopes'] = []
        self.__dict__['local_scopes'] = []

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

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        scope = self._get_scope(key)
        if scope is not None:
            return scope[key]
        raise NameError('name {} is not defined'.format(key))

    def __setitem__(self, key, val):
        (self._get_scope(key) or self.public_scopes[-1])[key] = val

    def __setattr__(self, key, val):
        if key in self.__dict__:
            super(_Variable, self).__setattr__(key, val)
        else:
            self[key] = val

    def __delitem__(self, key):
        scope = self._get_scope(key)
        if scope:
            del scope[key]

    def __delattr__(self, key):
        del self[key]

    def _add_to_scopes(self, scope, *args, **kwargs):
        for arg in args:
            scope[arg] = False
        for key in kwargs:
            scope[key] = kwargs[key]

    def add_local(self, *args, **kwargs):
        self._add_to_scopes(self.local_scopes[-1], *args, **kwargs)

    def add_private(self, *args, **kwargs):
        self._add_to_scopes(self.public_scopes[-1], *args, **kwargs)

    def add_public(self, *args, **kwargs):
        self._add_to_scopes(self.public_scopes[0], *args, **kwargs)

    def pushscope(self):
        self.public_scopes.append({})
        self.local_scopes.append({})

    def popscope(self, *args):
        self.public_scopes.pop()
        self.local_scopes.pop()
        if args:
            return args[0] if len(args) == 1 else args

    def release(self, mode='Normal', skeleton=None):
        if mode == 'Extended':
            pass
        elif mode == 'Like':
            pass
        elif mode == 'Except':
            pass
        else:
            for var in list(self.local_scopes[-1]) + list(self.public_scopes[-1]):
                del self[var]

class _Variable(object):
    def __init__(self, memvar, db):
        self.__dict__['memvar'] = memvar
        self.__dict__['db'] = db

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        try:
            return self.db._get_table_info(key).table.current_record
        except:
            pass
        table_info = self.db._get_table_info()
        if table_info is not None and key in table_info.table.field_names:
            return table_info.table.current_record[key]
        return self.memvar[key]

    def __setitem__(self, key, val):
        self.memvar[key] = val

    def __setattr__(self, key, val):
        if key in self.__dict__:
            super(_Variable, self).__setattr__(key, val)
        else:
            self.memvar[key] = val

class _Function(object):
    def __init__(self):
        self.__dict__['modules'] = []
        self.__dict__['dlls'] = []

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        for dll in self.dlls:
            if hasattr(dll, key):
                return getattr(dll, key)
        for module in self.modules:
            if not hasattr(module, key) or (hasattr(module, '_CLASSES') and key in module._CLASSES):
                continue
            obj = getattr(module, key)
            if isinstance(obj, (types.FunctionType, types.BuiltinFunctionType)):
                return obj
        for scope in M.public_scopes:
            if key in scope and isinstance(scope[key], Array):
                return scope[key]
        raise _EXCEPTION('{} is not a procedure'.format(key))

    def set_procedure(self, module, additive=False):
        if not additive:
            self.modules[:] = []
        elif module in self.modules:
            self.modules.remove(module)
        self.modules.insert(0, module)

    def release_procedure(self, *modules):
        for module in modules:
            self.modules.remove(module)

    def dll_declare(self, dllname, funcname, alias):
        # need something here to determine more about the dll file.
        try:
            dll = ctypes.CDLL(dllname)
        except:
            dll = ctypes.CDLL(ctypes.util.find_library(dllname))
        try:
            dll = next(d for d in self.dlls if d._name == dll._name)
        except:
            pass
        func = getattr(dll, funcname)
        alias = alias or funcname
        setattr(dll, alias, func)
        if dll not in self.dlls:
            self.dlls.append(dll)

    def dll_clear(self, *funcs):
        if not funcs:
            self.dlls = []
        else:
            for dll in self.dlls:
                for func in funcs:
                    if hasattr(dll, func):
                        delattr(dll, func)

class _Class(object):
    def __init__(self):
        self.modules = []

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        for module in self.modules:
            if hasattr(module, '_CLASSES') and key in module._CLASSES:
                return module._CLASSES[key]()
            elif hasattr(module, key) and inspect.isclass(getattr(module, key)):
                return getattr(module, key)
        raise KeyError(key)

    def set_procedure(self, module, additive=False):
        if not additive:
            self.modules[:] = []
        elif module in self.modules:
            self.modules.remove(module)
        self.modules.insert(0, module)

    def release_procedure(self, *modules):
        for module in modules:
            self.modules.remove(module)

def atline(search, string):
    return string[:string.find(search)+1].count('\r') + 1

def capslock(on=None):
    pass

def cdx(index, workarea):
    pass

def chrtran(expr, fchrs, rchrs):
     return ''.join(rchrs[fchrs.index(c)] if c in fchrs else c for c in expr)

def ctod(string):
    return dt.datetime.strptime(string, '%m/%d/%Y').date()

def ddeinitiate(service, topic):
    import dde
    import win32ui
    try:
        server = win32ui.GetApp().ddeServer
        conn = dde.CreateConversation(server)
        conn.ConnectTo(service, topic)
        return conn
    except dde.error:
        return -1

def ddesetoption(a, b):
    pass

def ddeterminate(a):
    pass

def ddesetservice(a, b, c=False):
    pass

def ddesettopic(a, b, c):
    pass

def dow_fix(weekday, firstday=0):
    return (weekday + 2 - (firstday or 1)) % 7 + 1

def dtos(dateobj):
    fmt = '%Y%m%d'
    if hasattr(dateobj, 'hour'):
        fmt += '%H%M%S'
    return dateobj.strftime(fmt)

def dtoc(dateobj):
    fmt = '%m/%d/%Y'
    if hasattr(dateobj, 'hour'):
        fmt += '%H:%M:%S'
    return dateobj.strftime(fmt)

def error(txt):
    raise _EXCEPTION(txt)

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

def getdir(dir='.', text='', caption='Select Text', flags=0, root_only=False):
    return QtGui.QFileDialog.getExistingDirectory(parent=S['_screen'], caption=caption, dir=dir)

def getfile(file_ext='', text='', button_caption='', button_type=0, title=''):
    filter = {
        '': '',
        'txt': 'File (*.txt)',
        'dbf': 'Table/DBF (*.dbf)',
    }.get(file_ext, '*.' + file_ext)
    t = QtGui.QFileDialog()
    t.setFilter('All Files (*.*);;' + filter)
    t.selectFilter(filter or 'All Files (*.*);;')
    if text:
        (next(x for x in t.findChildren(QtGui.QLabel) if x.text() == 'File &name:')).setText(text)
    if button_caption:
        t.setLabelText(QtGui.QFileDialog.Accept, button_caption)
    if title:
        t.setWindowTitle(title)
    t.exec_()
    return t.selectedFiles()[0]

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
        raise _EXCEPTION('not implemented')
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
    return getfile(file_ext=ext, title=caption)

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

    flags=0
    title='vfp2py'
    if arg1 is not None:
        if isinstance(arg1, _str):
            title = arg1
            if arg2 is not None:
                flags = arg2
        else:
            flags = arg1
            if arg2 is not None:
                title = arg2
    flags = int(flags) & 1023

    buttons = {
        OK_ONLY: ((OK,), OK),
        OK_CANCEL: ((OK, CANCEL), CANCEL),
        ABORT_RETRY_IGNORE: ((ABORT, RETRY, IGNORE), IGNORE),
        YES_NO_CANCEL: ((YES, NO, CANCEL), CANCEL),
        YES_NO: ((YES, NO), NO),
        RETRY_CANCEL: ((RETRY, CANCEL), CANCEL)
    }[flags & 15]

    buttonobj = buttons[0][0]
    for button in buttons[0][1:]:
        buttonobj |= button

    icon = {
        NOICON: QtGui.QMessageBox.NoIcon,
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
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(closebox)
        timer.start(float(timeout)*1000)
        timeout = timer
    button = msg_box.exec_()
    if timeout and timeout.isActive():
        timeout.stop()
    retval = retval[0]
    center_widget(msg_box)
    return {
        OK: RETURN_OK,
        CANCEL: RETURN_CANCEL,
        ABORT: RETURN_ABORT,
        RETRY: RETURN_RETRY,
        IGNORE: RETURN_IGNORE,
        YES: RETURN_YES,
        NO: RETURN_NO
    }[button] if retval != -1 else -1


def pcount():
    return PCOUNTS[-1]

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
    return string[:string.rfind(search)+1].count('\r') + 1

def rgb(red, green, blue):
    return QtGui.QColor(red, green, blue)

def seconds():
    now = dt.datetime.now()
    return (now - dt.datetime.combine(now, dt.time(0, 0))).seconds

def str(num, length=10, decimals=0):
    length = int(length)
    string = '{{:.{}f}}'.format(int(decimals)).format(num)
    if len(string) > length and len(string) - (decimals - 1) <= length:
        string = string[:length]
    elif len(string) > length:
        string = string.split('.')[0]
        if len(string) >= length:
            string = '{:E}'.format(num)
            groups = list(re.match(r'(\d.)(\d+)(E[+-])0*(\d+)', string).groups())
            trim = sum(len(x) for x in groups) - length
            if trim > 0:
                groups[1] = groups[1][:-trim]
            string = ''.join(groups)
    string = string.rjust(length)
    return string if len(string) == length else '*' * length

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

    if flag == 2:
        output = string.encode('utf-16')
    elif flag == 4:
        output = b'\xef\xbb\xbf' + string.encode('utf-8')
    else:
        output = string

    try:
        with open(filename, mode) as fid:
            fid.write(output)
        return len(output)
    except:
        return 0

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
    return string[:int(start)-1] + repl + string[int(start)-1+int(num_replaced):]

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
            raise _EXCEPTION('')
        column_info = values[0].cursor_description
        columns = []
        for i, column in enumerate(column_info):
            field_name = column[0][:10]
            field_type = {
                int: 'N',
                _str: 'C',
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
        DB.use(None, DB.select_function(cursor_name), None)
        DB.create_table(cursor_name + '.dbf', columns, 'free')
        for value in values:
            DB.insert(cursor_name, tuple(value))
        DB.goto(cursor_name, 0)
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

SYS2000iter = None
def vfp_sys(funcnum, *args):
    global SYS2000iter
    if funcnum == 16:
        import imp
        if hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__"):
            return os.path.dirname(sys.executable)
        return os.path.dirname(sys.argv[0])
    if funcnum == 2000:
        #seems to implement FindFirstFile and FindNextFile in win32api
        if len(args) == 1:
            skel, = args
            next_file = False
        else:
            skel, next_file = args[:2]
        if next_file:
            try:
                return next(SYS2000iter)
            except:
                return ''
        SYS2000iter = glob.iglob(skel)
        return vfp_sys(2000, skel, 1)


TYPE_MAP = {
    _str: 'C',
    dt.date: 'D',
    bool: 'L',
    int: 'N',
    float: 'N',
    dt.datetime: 'T',
    type(None): 'X',
}
if sys.version_info < (3,):
    TYPE_MAP[unicode] = 'C'

def vartype(var):
    return TYPE_MAP.get(type(var), 'O')

def version(ver_type=4):
    if ver_type == 4:
        return 'Not FoxPro 9'
    if ver_type == 5:
        return 900

def wait(msg, to=None, window=[-1, -1], nowait=False, noclear=False, timeout=-1):
    pass
def gather(val=None, fields=None, fieldstype=None, memo=None):
    DB._update_from(val)

def scatter(totype=None, name=None, fields=None, fieldstype=None, memo=False, blank=False):
    record = DB._current_record_copy()
    if totype == 'name':
        return record

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
    elif setword in ('cursor', 'deleted', 'escape', 'exact', 'multilocks', 'near', 'status', 'status bar', 'talk', 'unique'):
        if args[0].lower() not in ('on', 'off'):
            raise ValueError('Bad argument: {}'.format(args[0]))
        settings[0] = args[0].upper()
    elif setword in ('index', 'refresh'):
        settings = args
    elif setword == 'procedure':
        module = importlib.import_module(args[0])
        F.set_procedure(module, additive=kwargs.get('additive', False))
        C.set_procedure(module, additive=kwargs.get('additive', False))
    SET_PROPS[setword] = settings

def text(text_lines, show=True):
    text = ''.join(l.strip() for l in text_lines)
    if show:
        print(text)
    return text

def create_object(objtype, *args, **kwargs):
    objtype = objtype.title()
    frame = inspect.getouterframes(inspect.currentframe())[2][0]
    if objtype in frame.f_globals:
        return frame.f_globals[objtype](*args, **kwargs)
    try:
        return C[objtype]()
    except:
        pass
    try:
        return win32com.client.Dispatch(objtype)
    except:
        pass
    raise _EXCEPTION('class definition \'{}\' not found'.format(objtype))

def clearall():
    pass

def clear(*args):
    pass

DB = DatabaseContext()
M = _Memvar()
S = _Variable(M, DB)
F = _Function()
C = _Class()

def module(module_name):
    return __import__(module_name.lower())

error_func = None
M.pushscope()
M.add_public('_screen')
S._screen = MainWindow()
S._screen.caption = 'VFP To Python'

def _parameters(scope_func, *varnames):
    def decorator(fn):
        fn_args = fn.__code__.co_varnames
        if len(fn_args) == 1 and fn_args[0] == 'self' and varnames:
            @functools.wraps(fn)
            def scoper(self, *args):
                global PARAMETERS
                M.pushscope()
                PARAMETERS = len(args)
                PCOUNTS.append(PARAMETERS)
                kwargs = {name: arg for name, arg in zip(varnames, args)}
                args = varnames[len(args):]
                scope_func(*args, **kwargs)
                retval = fn(self)
                PCOUNTS.pop()
                M.popscope()
                return retval
        elif varnames:
            @functools.wraps(fn)
            def scoper(*args):
                global PARAMETERS
                M.pushscope()
                PARAMETERS = len(args)
                PCOUNTS.append(PARAMETERS)
                kwargs = {name: arg for name, arg in zip(varnames, args)}
                args = varnames[len(args):]
                scope_func(*args, **kwargs)
                retval = fn()
                PCOUNTS.pop()
                M.popscope()
                return retval
        else:
            @functools.wraps(fn)
            def scoper(*args):
                global PARAMETERS
                M.pushscope()
                PARAMETERS = 0
                PCOUNTS.append(PARAMETERS)
                retval = fn(*args)
                PCOUNTS.pop()
                M.popscope()
                return retval
        scoper.__name__ = fn.__name__
        return scoper
    return decorator

def parameters(*varnames):
    return _parameters(M.add_private, *varnames)

def lparameters(*varnames):
    return _parameters(M.add_local, *varnames)

def vfpclass(fn):
    if '_CLASSES' not in fn.__globals__:
        fn.__globals__['_CLASSES'] = {}
    fn.__globals__['_CLASSES'][fn.__name__] = fn
    @functools.wraps(fn)
    def double_caller(*args, **kwargs):
        return fn()(*args, **kwargs)
    fn.__globals__[fn.__name__ + 'Type'] = fn
    return double_caller

set('procedure', 'vfp2py.vfpfunc', set_value=True)
