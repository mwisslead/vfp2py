# coding=utf-8
from __future__ import division, print_function

import datetime as dt
import math
import os
import random

import faker
from vfp2py import vfpfunc
from vfp2py.vfpfunc import DB, Array, C, F, M, S, lparameters, parameters, vfpclass


@lparameters()
def MAIN():
    pass


@lparameters()
def select_tests():
    assert DB.select_function(0 if vfpfunc.set('compatible') == 'OFF' else None) == 1
    assert DB.select_function(0) == 1
    assert DB.select_function(1) == 32767
    assert DB.select_function(2) == 0
    assert DB.select_function('test') == 0


@lparameters()
def chr_tests():
    assert ord('\x00'[0]) == 0


@lparameters()
def set_tests():
    assert vfpfunc.set('compatible') == 'OFF'
    assert vfpfunc.set('compatible', 1) == 'PROMPT'


@lparameters()
def used_tests():
    assert DB.used('test') == False


@lparameters()
def date_tests():
    M.add_local('somedate')
    S.somedate = dt.date(2017, 6, 30)
    assert S.somedate == dt.date(2017, 6, 30)
    assert vfpfunc.dow_fix(S.somedate.weekday()) == 6
    assert S.somedate.strftime('%A') == 'Friday'
    assert S.somedate.month == 6
    assert S.somedate.strftime('%B') == 'June'
    assert S.somedate.strftime('%d %B %Y') == '30 June 2017'
    assert vfpfunc.dtos(S.somedate) == '20170630'
    assert vfpfunc.dtoc(S.somedate) == '06/30/2017'
    assert len(dt.datetime.now().time().strftime('%H:%M:%S')) == 8
    assert len(dt.datetime.now().time().strftime('%H:%M:%S.%f')[:11]) == 11
    assert dt.datetime.combine(S.somedate, dt.datetime.min.time()) == dt.datetime(2017, 6, 30, 0)
    assert vfpfunc.gomonth(S.somedate, -4) == dt.date(2017, 2, 28)
    assert vfpfunc.vartype(S.somedate) == 'D'
    assert vfpfunc.vartype(dt.datetime.combine(S.somedate, dt.datetime.min.time())) == 'T'


@lparameters()
def math_tests():
    M.add_local('num_value')
    S.num_value = math.pi
    assert round(math.pi, 2) == 3.14
    assert abs(math.tan(math.radians(45)) - 1) < 0.001
    assert abs(math.sin(math.radians(90)) - 1) < 0.001
    assert abs(math.cos(math.radians(90)) - 0) < 0.001
    assert abs(math.cos(math.radians(45)) - math.sqrt(2) / 2) < 0.001
    assert 0 < random.random() and random.random() < 1
    assert (5 % 2) == 1

    M.add_local('stringval')
    S.stringval = '1e5'
    assert float(S.stringval) == 100000
    assert vfpfunc.vartype(S.num_value) == 'N'
    assert not ((True or True) and False)
    assert True or False and True


@lparameters()
def string_tests():
    S.cstring = 'AAA  aaa, BBB bbb, CCC ccc.'
    assert vfpfunc.vartype(S.cstring) == 'C'
    assert len([w for w in S.cstring.split() if w]) == 6
    assert len([w for w in S.cstring.split(',') if w]) == 3
    assert len([w for w in S.cstring.split('.') if w]) == 1
    assert vfpfunc.getwordnum(S.cstring, 2) == 'aaa,'
    assert vfpfunc.getwordnum(S.cstring, 2, ',') == ' BBB bbb'
    assert vfpfunc.getwordnum(S.cstring, 2, '.') == ''
    assert vfpfunc.like('Ab*t.???', 'About.txt')
    assert not vfpfunc.like('Ab*t.???', 'about.txt')
    assert not ''[:1].isalpha()
    assert 'a123'[:1].isalpha()
    assert not '1abc'[:1].isalpha()
    assert not ''[:1].islower()
    assert 'test'[:1].islower()
    assert not 'Test'[:1].islower()
    assert not ''[:1].isdigit()
    assert '1abc'[:1].isdigit()
    assert not 'a123'[:1].isdigit()
    assert not ''[:1].isupper()
    assert 'Test'[:1].isupper()
    assert not 'test'[:1].isupper()
    assert vfpfunc.isblank('')
    assert not vfpfunc.isblank('test')
    assert vfpfunc.isblank(None)
    S.cstring = ' AAA   '
    assert S.cstring.strip() == 'AAA'
    assert S.cstring.rstrip() == ' AAA'
    assert S.cstring.lstrip() == 'AAA   '
    assert S.cstring.rstrip() == S.cstring.rstrip()
    assert vfpfunc.strextract('This {{is}} a {{template}}', '{{', '}}') == 'is'
    assert vfpfunc.strextract('This {{is}} a {{template}}', '{{', '}}', 2) == 'template'
    assert vfpfunc.strextract('This {{is}} a {{template}}', '{{is}}') == ' a {{template}}'
    assert vfpfunc.strextract('This {{is}} a {{template}}', '{{IS}}', '', 1, 1) == ' a {{template}}'
    assert '123AAbbB'.lower().find('aab'.lower()) + 1 == 4
    S.cstring = vfpfunc.text(['      123AAbbbB',
                              '      TESTTEST',
                              '      TEXTLINES',
                              '   '], show=False)
    assert S.cstring == '123AAbbbBTESTTESTTEXTLINES'
    S.cstring = '123AAbbbB\r\nTESTTEST\r\nTEXTLINES'
    assert vfpfunc.atline('T', S.cstring) == 2
    assert vfpfunc.ratline('T', S.cstring) == 3


@lparameters()
def path_tests():
    assert vfpfunc.home() == os.getcwd()
    S.handle = open('test_lib_file', 'w')
    S.handle.close()
    assert not vfpfunc.isblank(vfpfunc.locfile('test_lib_file'))
    os.chdir('..')
    assert vfpfunc.home() != os.getcwd()
    assert not vfpfunc.isblank(vfpfunc.locfile('test_lib_file'))
    os.remove(os.path.join(vfpfunc.home(), 'test_lib_file'))


@lparameters()
def misc_tests():
    assert vfpfunc.version() == 'Not FoxPro 9'
    assert vfpfunc.version(4) == vfpfunc.version()
    assert vfpfunc.version(5) == 900


@lparameters('seed')
def _add_db_record():
    M.add_local('fake', 'fake_name', 'fake_st', 'fake_quantity', 'fake_received')
    S.fake = faker.Faker()
    S.fake.seed(S.seed)
    S.fake_name = S.fake.name()
    S.fake_st = S.fake.state_abbr()
    S.fake_quantity = S.fake.random_int(0, 100)
    S.fake_received = S.fake.boolean()
    DB.insert('report', (S.fake_name, S.fake_st, S.fake_quantity, S.fake_received))


@lparameters('sqlconn', 'seed')
def _sqlexec_add_record():
    M.add_local('fake', 'fake_name', 'fake_st', 'fake_quantity', 'fake_received')
    S.fake = faker.Faker()
    S.fake.seed(S.seed)
    S.fake_name = S.fake.name()
    S.fake_st = S.fake.state_abbr()
    S.fake_quantity = S.fake.random_int(0, 100)
    S.fake_received = S.fake.boolean()
    S.sqlcmd = "insert into REPORT values ('" + S.fake_name + "','" + S.fake_st + "'," + vfpfunc.str(S.fake_quantity).strip() + ',' + vfpfunc.str(int(S.fake_received)).strip() + ')'
    print(S.sqlcmd)
    return vfpfunc.sqlexec(S.sqlconn, S.sqlcmd)


@lparameters()
def database_tests():
    # FIX ME: SET SAFETY OFF
    # FIX ME: SET ASSERTS ON
    try:
        DB.create_table('report', 'name c(50); st c(2); quantity n(5, 0); received l', 'free')
        assert os.path.isfile('report.dbf')
        assert DB.used('report')
        try:
            DB.use('report', 0, 'shared')
            assert False
        except Exception as err:
            S.oerr = vfpfunc.Exception.from_pyexception(err)
            print(S.oerr.message)
            assert S.oerr.message == 'File is in use.'
        _add_db_record(0)
        _add_db_record(1)
        _add_db_record(2)
        _add_db_record(3)
        assert DB.cpdbf() == 0
        assert DB.fcount() == 4
        DB.alter_table('report', 'add', 'age n(3, 0)')
        assert DB.fcount() == 5
        assert DB.field(2) == 'st'
        assert not DB.found()
        DB.goto(None, 0)
        M.add_local('loopcount')
        S.loopcount = 0
        for _ in DB.scanner(scope=('rest',)):
            assert len(S.name.strip()) > 0
            S.loopcount += 1
        assert S.loopcount == 4
        DB.goto(None, 3)
        S.loopcount = 0
        for _ in DB.scanner(condition=lambda: S.st.strip() == 'ID', scope=('all',)):
            assert len(S.name.strip()) > 0
            S.loopcount += 1
        assert S.loopcount == 2
        S.loopcount = 0
        for _ in DB.scanner(condition=lambda: S.st.strip() == 'ID', scope=('rest',)):
            assert len(S.name.strip()) > 0
            S.loopcount += 1
        assert S.loopcount == 0
        DB.goto(None, 0)
        S.loopcount = 0
        for _ in DB.scanner(condition=lambda: S.st.strip() == 'ID', scope=('rest',)):
            assert len(S.name.strip()) > 0
            S.loopcount += 1
        assert S.loopcount == 2
        del M.loopcount
        assert S.name.strip() == 'Norma Fisher', S.name.strip() + ' should be Norma Fisher'
        assert DB.recno() == 1
        S.report_record = vfpfunc.scatter(totype='name')
        assert S.report_record.name.strip() == 'Norma Fisher', S.report_record.name.strip() + ' should be Norma Fisher'
        DB.goto(None, -1)
        assert S.name.strip() == 'Joshua Wood', S.name.strip() + ' should be Joshua Wood'
        assert S.report_record.name.strip() == 'Norma Fisher', S.report_record.name.strip() + ' should be Norma Fisher'
        assert DB.recno() == 4
        DB.goto(None, 1)
        DB.locate(for_cond=lambda: S.st == 'ID')
        assert S.name.strip() == 'Norma Fisher', S.name.strip() + ' should be Norma Fisher'
        assert DB.found()
        DB.continue_locate()
        assert S.name.strip() == 'Ryan Gallagher', S.name.strip() + ' should be Ryan Gallagher'
        DB.continue_locate()
        assert DB.eof()
        assert DB.recno() == DB.reccount() + 1
        assert not DB.found()
        S.countval = DB.count(None, ('all',), for_cond=lambda: S.quantity > 60)
        assert S.countval == 2
        assert DB.eof()
        S.sumval = DB.sum(None, ('rest',), lambda: math.sqrt(S.quantity + 205), for_cond=lambda: S.quantity > 50, while_cond=lambda: S.quantity != 63)
        assert S.sumval == 0
        DB.goto(None, 0)
        S.sumval = DB.sum(None, ('rest',), lambda: math.sqrt(S.quantity + 205), for_cond=lambda: S.quantity > 50, while_cond=lambda: S.quantity != 63)
        assert S.sumval == 17 + 16
        DB.index_on('st', 'st', 'ascending', True, False, False)
        DB.seek(None, 'CA')
        assert S.st.strip() == 'CA'
        DB.goto(None, 0)
        DB.delete_record(None, ('rest',), for_cond=lambda: S.quantity > 60)
        DB.pack('both', None, None)
        DB.goto(None, 0)
        assert DB.reccount() == 2
        DB.replace('report', ('next', 1), 'name', 'N/A')
        assert S.name.strip() == 'N/A'
        DB.replace(None, ('all',), 'name', 'Not Available')
        assert DB.recno() == DB.reccount() + 1
        DB.goto(None, -1)
        assert S.name.strip() == 'Not Available'
        DB.zap(None)
        assert DB.reccount() == 0
        DB.copy_structure('report2')
        DB.use('report2', 0, 'shared', alias='somethingelse')
        assert DB.alias() == 'report'
        DB.select('report2')
        assert DB.alias() == 'somethingelse'
        assert DB.fcount() == 5
        DB.alter_table('report2', 'drop', 'st')
        assert DB.fcount() == 4
        assert S.report_record.name.strip() == 'Norma Fisher', S.report_record.name.strip() + ' should be Norma Fisher'
        DB.append(None, False)
        vfpfunc.gather(val=S.report_record)
        assert S.name.strip() == 'Norma Fisher', S.name.strip() + ' should be Norma Fisher'
        assert DB.dbf() == 'report2.dbf'
        DB.use(None, DB.select_function('report2'), None)
        DB.use(None, DB.select_function('report'), None)
        os.remove('report2.dbf')
    except Exception as err:
        S.err = vfpfunc.Exception.from_pyexception(err)
        print(S.err.message)
        DB.browse()
        raise
    finally:
        os.remove('report.dbf')
    S.sqlconn = vfpfunc.sqlconnect('testodbc')
    assert S.sqlconn > 0
    assert vfpfunc.sqlexec(S.sqlconn, 'CREATE TABLE REPORT (NAME varchar(50), ST char(2), QUANTITY int(5), RECEIVED bit)') > 0
    assert _sqlexec_add_record(S.sqlconn, 0) > 0
    assert _sqlexec_add_record(S.sqlconn, 1) > 0
    assert _sqlexec_add_record(S.sqlconn, 2) > 0
    assert _sqlexec_add_record(S.sqlconn, 3) > 0
    assert vfpfunc.sqlexec(S.sqlconn, 'SELECT * FROM REPORT')
    DB.select('sqlresult')
    assert S.name.strip() == 'Norma Fisher'
    vfpfunc.sqlcommit(S.sqlconn)
    vfpfunc.sqldisconnect(S.sqlconn)
    S.sqlconn = vfpfunc.sqlstringconnect('dsn=testodbc')
    assert S.sqlconn > 0
    assert vfpfunc.sqltables(S.sqlconn) > 0
    DB.select('sqlresult')
    assert S.table_name.strip().lower() == 'report'
    assert vfpfunc.sqlexec(S.sqlconn, 'DELETE FROM REPORT;')
    assert vfpfunc.sqlrollback(S.sqlconn)
    assert vfpfunc.sqlexec(S.sqlconn, 'SELECT * FROM REPORT')
    DB.select('sqlresult')
    assert S.name.strip() == 'Norma Fisher'
    assert vfpfunc.sqlexec(S.sqlconn, 'DROP TABLE REPORT') > 0
    vfpfunc.sqlcommit(S.sqlconn)
    vfpfunc.sqldisconnect(S.sqlconn)
    # FIX ME: close tables


@lparameters('arg1', 'arg2')
def user_defined_function():
    assert vfpfunc.pcount() == 1
    assert vfpfunc.PARAMETERS == 1
    user_defined_function2()
    assert vfpfunc.PARAMETERS == 0
    assert vfpfunc.pcount() == 1


@lparameters('arg1')
def user_defined_function2():
    pass


@lparameters()
def scope_tests():
    M.add_public(somearray=Array(2, 5))
    M.add_public(**{'def': Array(10)})
    assert F['def'](1) == False
    S.somearray[1, 4] = 3
    assert F.somearray(1, 4) == 3
    M.add_private('test', somearray=Array(2, 5))
    del M.nonexistantvariable

    vfpfunc.set('procedure', 'time', set_value=True)
    print(F.localtime())

    vfpfunc.set('procedure', 'argparse', set_value=True)
    S.t = vfpfunc.create_object('Namespace')

    user_defined_function(False)


@vfpclass
def Someclass():
    BaseClass = vfpfunc.Custom

    class Someclass(BaseClass):
        @lparameters()
        def _assign(self):
            BaseClass._assign(self)
    return Someclass


@lparameters()
def class_tests():
    S.obj = Someclass()
