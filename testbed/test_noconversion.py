from vfp2py.vfpfunc import variable as vfpvar

def scope_test():
    vfpvar['test'] = 3
    assert vfpvar.test == 3
