from vfp2py.vfpfunc import S, F

def scope_test():
    S['test'] = 3
    assert S.test == 3
    S.test = 4
    assert S['test'] == 4
    func = lambda: 3
    F['func'] = func
    assert F.func == func
    assert F.func() == 3
