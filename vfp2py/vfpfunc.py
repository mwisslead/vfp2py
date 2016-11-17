import builtins
import datetime
import os

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
