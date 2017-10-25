from __future__ import division, print_function

import datetime as dt
import math
import os
import random

import faker

from vfp2py import vfpfunc
from vfp2py.vfpfunc import variable as vfpvar


def _program_main():
    pass


def select_tests():
    assert vfpfunc.db.select_function(0 if vfpfunc.set('compatible') == 'OFF' else None) == 1
    assert vfpfunc.db.select_function(0) == 1
    assert vfpfunc.db.select_function(1) == 32767
    assert vfpfunc.db.select_function(2) == 0
    assert vfpfunc.db.select_function('test') == 0


def chr_tests():
    assert ord('\x00'[0]) == 0


def set_tests():
    assert vfpfunc.set('compatible') == 'OFF'
    assert vfpfunc.set('compatible', 1) == 'PROMPT'


def used_tests():
    assert vfpfunc.db.used('test') == False


def date_tests():
    somedate = False  # LOCAL Declaration
    somedate = dt.date(2017, 6, 30)
    assert somedate == dt.date(2017, 6, 30)
    assert vfpfunc.dow_fix(somedate.weekday()) == 6
    assert somedate.strftime('%A') == 'Friday'
    assert somedate.month == 6
    assert somedate.strftime('%B') == 'June'
    assert somedate.strftime('%d %B %Y') == '30 June 2017'
    assert len(dt.datetime.now().time().strftime('%H:%M:%S')) == 8
    assert len(dt.datetime.now().time().strftime('%H:%M:%S.%f')[:11]) == 11
    assert dt.datetime.combine(somedate, dt.datetime.min.time()) == dt.datetime(2017, 6, 30, 0)
    assert vfpfunc.gomonth(somedate, -4) == dt.date(2017, 2, 28)
    assert vfpfunc.vartype(somedate) == 'D'
    assert vfpfunc.vartype(dt.datetime.combine(somedate, dt.datetime.min.time())) == 'T'


def math_tests():
    num_value = False  # LOCAL Declaration
    num_value = math.pi
    assert round(math.pi, 2) == 3.14
    assert abs(math.tan(math.radians(45)) - 1) < 0.001
    assert abs(math.sin(math.radians(90)) - 1) < 0.001
    assert abs(math.cos(math.radians(90)) - 0) < 0.001
    assert abs(math.cos(math.radians(45)) - math.sqrt(2) / 2) < 0.001
    assert 0 < random.random() and random.random() < 1

    stringval = False  # LOCAL Declaration
    stringval = '1e5'
    assert float(stringval) == 100000
    assert vfpfunc.vartype(num_value) == 'N'


def string_tests():
    vfpvar.pushscope()
    vfpvar['cstring'] = 'AAA  aaa, BBB bbb, CCC ccc.'
    assert vfpfunc.vartype(vfpvar['cstring']) == 'C'
    assert len([w for w in vfpvar['cstring'].split() if w]) == 6
    assert len([w for w in vfpvar['cstring'].split(',') if w]) == 3
    assert len([w for w in vfpvar['cstring'].split('.') if w]) == 1
    assert vfpfunc.getwordnum(vfpvar['cstring'], 2) == 'aaa,'
    assert vfpfunc.getwordnum(vfpvar['cstring'], 2, ',') == ' BBB bbb'
    assert vfpfunc.getwordnum(vfpvar['cstring'], 2, '.') == ''
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
    vfpvar['cstring'] = ' AAA   '
    assert vfpvar['cstring'].strip() == 'AAA'
    assert vfpvar['cstring'].rstrip() == ' AAA'
    assert vfpvar['cstring'].lstrip() == 'AAA   '
    assert vfpvar['cstring'].lstrip() == vfpvar['cstring'].lstrip()
    assert vfpfunc.strextract('This {{is}} a {{template}}', '{{', '}}') == 'is'
    assert vfpfunc.strextract('This {{is}} a {{template}}', '{{', '}}', 2) == 'template'
    assert vfpfunc.strextract('This {{is}} a {{template}}', '{{is}}') == ' a {{template}}'
    assert vfpfunc.strextract('This {{is}} a {{template}}', '{{IS}}', '', 1, 1) == ' a {{template}}'
    vfpvar.popscope()


def path_tests():
    vfpvar.pushscope()
    assert vfpfunc.home() == os.getcwd()
    vfpvar['handle'] = open('test_lib_file', 'w')
    vfpvar['handle'].close()
    assert not vfpfunc.isblank(vfpfunc.locfile('test_lib_file'))
    os.chdir('..')
    assert vfpfunc.home() != os.getcwd()
    assert not vfpfunc.isblank(vfpfunc.locfile('test_lib_file'))
    os.remove(os.path.join(vfpfunc.home(), 'test_lib_file'))
    vfpvar.popscope()


def _add_db_record(seed=False):
    fake = fake_name = fake_st = fake_quantity = fake_received = False  # LOCAL Declaration
    fake = faker.Faker()
    fake.seed(seed)
    fake_name = fake.name()
    fake_st = fake.state_abbr()
    fake_quantity = fake.random_int(0, 100)
    fake_received = fake.boolean()
    vfpfunc.db.insert('report', (fake_name, fake_st, fake_quantity, fake_received))


def _sqlexec_add_record(sqlconn=False, seed=False):
    vfpvar.pushscope()
    fake = fake_name = fake_st = fake_quantity = fake_received = False  # LOCAL Declaration
    fake = faker.Faker()
    fake.seed(seed)
    fake_name = fake.name()
    fake_st = fake.state_abbr()
    fake_quantity = fake.random_int(0, 100)
    fake_received = fake.boolean()
    vfpvar['sqlcmd'] = "insert into REPORT values ('" + fake_name + "','" + fake_st + "'," + vfpfunc.num_to_str(
        fake_quantity).strip() + ',' + vfpfunc.num_to_str(int(fake_received)).strip() + ')'
    print(vfpvar['sqlcmd'])
    return vfpvar.popscope(vfpfunc.sqlexec(sqlconn, vfpvar['sqlcmd']))


def database_tests():
    vfpvar.pushscope()
    # FIX ME: SET SAFETY OFF
    # FIX ME: SET ASSERTS ON
    try:
        vfpfunc.db.create_table(
            'report', 'name c(50); st c(2); quantity n(5, 0); received l', 'free')
        assert os.path.isfile('report.dbf')
        assert vfpfunc.db.used('report')
        try:
            vfpfunc.db.use('report', 0, 'shared')
            assert False
        except Exception as oerr:
            # vfpfunc.pyexception_to_foxexception(oerr)
            print(oerr.message)
            assert oerr.message == 'File is in use.'
        _add_db_record(0)
        _add_db_record(1)
        _add_db_record(2)
        _add_db_record(3)
        assert vfpfunc.db.fcount() == 4
        vfpfunc.db.alter_table('report', 'add', 'age n(3, 0)')
        assert vfpfunc.db.fcount() == 5
        assert vfpfunc.db.field(2) == 'st'
        assert not vfpfunc.db.found()
        vfpfunc.db.goto(None, 0)
        loopcount = False  # LOCAL Declaration
        loopcount = 0
        for _ in vfpfunc.db.scanner():
            assert len(vfpvar['name'].strip()) > 0
            loopcount += 1
        assert loopcount == 4
        loopcount = 0
        for _ in vfpfunc.db.scanner(lambda: vfpvar['st'].strip() == 'ID'):
            assert len(vfpvar['name'].strip()) > 0
            loopcount += 1
        assert loopcount == 2
        del loopcount
        assert vfpvar['name'].strip() == 'Norma Fisher', vfpvar[
            'name'].strip() + ' should be Norma Fisher'
        assert vfpfunc.db.recno() == 1
        vfpfunc.db.goto(None, -1)
        assert vfpvar['name'].strip() == 'Joshua Wood', vfpvar[
            'name'].strip() + ' should be Joshua Wood'
        assert vfpfunc.db.recno() == 4
        vfpfunc.db.goto(None, 1)
        vfpfunc.db.locate(for_cond=lambda: vfpvar['st'] == 'ID', nooptimize=None)
        assert vfpvar['name'].strip() == 'Norma Fisher', vfpvar[
            'name'].strip() + ' should be Norma Fisher'
        assert vfpfunc.db.found()
        vfpfunc.db.continue_locate()
        assert vfpvar['name'].strip() == 'Ryan Gallagher', vfpvar[
            'name'].strip() + ' should be Ryan Gallagher'
        vfpfunc.db.continue_locate()
        assert vfpfunc.db.eof()
        assert vfpfunc.db.recno() == vfpfunc.db.reccount() + 1
        assert not vfpfunc.db.found()
        vfpvar['countval'] = vfpfunc.db.count(
            None, ('all',), for_cond=lambda: vfpvar['quantity'] > 60)
        assert vfpvar['countval'] == 2
        assert vfpfunc.db.eof()
        vfpvar['sumval'] = vfpfunc.db.sum(None, ('rest',), lambda: math.sqrt(
            vfpvar['quantity'] + 205), for_cond=lambda: vfpvar['quantity'] > 50, while_cond=lambda: vfpvar['quantity'] != 63)
        assert vfpvar['sumval'] == 0
        vfpfunc.db.goto(None, 0)
        vfpvar['sumval'] = vfpfunc.db.sum(None, ('rest',), lambda: math.sqrt(
            vfpvar['quantity'] + 205), for_cond=lambda: vfpvar['quantity'] > 50, while_cond=lambda: vfpvar['quantity'] != 63)
        assert vfpvar['sumval'] == 17 + 16
        vfpfunc.db.index_on('st', 'st', 'ascending', True, False, False)
        vfpfunc.db.seek(None, 'CA')
        assert vfpvar['st'].strip() == 'CA'
        vfpfunc.db.goto(None, 0)
        vfpfunc.db.delete_record(None, ('rest',), for_cond=lambda: vfpvar['quantity'] > 60)
        vfpfunc.db.pack('both', None, None)
        vfpfunc.db.goto(None, 0)
        assert vfpfunc.db.reccount() == 2
        vfpfunc.db.replace('report', ('next', 1), 'name', 'N/A')
        assert vfpvar['name'].strip() == 'N/A'
        vfpfunc.db.replace(None, ('all',), 'name', 'Not Available')
        assert vfpfunc.db.recno() == vfpfunc.db.reccount() + 1
        vfpfunc.db.goto(None, -1)
        assert vfpvar['name'].strip() == 'Not Available'
        vfpfunc.db.zap(None)
        assert vfpfunc.db.reccount() == 0
        vfpfunc.db.copy_structure('report2')
        vfpfunc.db.use('report2', 0, 'shared')
        assert vfpfunc.db.alias() == 'report'
        vfpfunc.db.select('report2')
        assert vfpfunc.db.alias() == 'report2'
        assert vfpfunc.db.fcount() == 5
        vfpfunc.db.alter_table('report2', 'drop', 'st')
        assert vfpfunc.db.fcount() == 4
        vfpfunc.db.use(None, None, None)
        os.remove('report2.dbf')
    except Exception as err:
        # vfpfunc.pyexception_to_foxexception(err)
        print(err.message)
        vfpfunc.db.browse()
        raise
    finally:
        os.remove('report.dbf')
    vfpvar['sqlconn'] = vfpfunc.sqlconnect('testodbc')
    assert vfpvar['sqlconn'] > 0
    assert vfpfunc.sqlexec(vfpvar[
                           'sqlconn'], 'CREATE TABLE REPORT (NAME varchar(50), ST char(2), QUANTITY int(5), RECEIVED bit)') > 0
    assert _sqlexec_add_record(vfpvar['sqlconn'], 0) > 0
    assert _sqlexec_add_record(vfpvar['sqlconn'], 1) > 0
    assert _sqlexec_add_record(vfpvar['sqlconn'], 2) > 0
    assert _sqlexec_add_record(vfpvar['sqlconn'], 3) > 0
    assert vfpfunc.sqlexec(vfpvar['sqlconn'], 'SELECT * FROM REPORT')
    vfpfunc.db.select('sqlresult')
    assert vfpvar['name'].strip() == 'Norma Fisher'
    vfpfunc.sqlcommit(vfpvar['sqlconn'])
    vfpfunc.sqldisconnect(vfpvar['sqlconn'])
    vfpvar['sqlconn'] = vfpfunc.sqlstringconnect('dsn=testodbc')
    assert vfpvar['sqlconn'] > 0
    assert vfpfunc.sqltables(vfpvar['sqlconn']) > 0
    vfpfunc.db.select('sqlresult')
    assert vfpvar['table_name'].strip().lower() == 'report'
    assert vfpfunc.sqlexec(vfpvar['sqlconn'], 'DELETE FROM REPORT;')
    assert vfpfunc.sqlrollback(vfpvar['sqlconn'])
    assert vfpfunc.sqlexec(vfpvar['sqlconn'], 'SELECT * FROM REPORT')
    vfpfunc.db.select('sqlresult')
    assert vfpvar['name'].strip() == 'Norma Fisher'
    assert vfpfunc.sqlexec(vfpvar['sqlconn'], 'DROP TABLE REPORT') > 0
    vfpfunc.sqlcommit(vfpvar['sqlconn'])
    vfpfunc.sqldisconnect(vfpvar['sqlconn'])
    vfpvar.popscope()
