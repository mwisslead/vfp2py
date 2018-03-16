from vfp2py.vfpfunc import S

def scope_test():
    S['test'] = 3
    assert S.test == 3
