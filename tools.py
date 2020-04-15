import json
import os
from basics import klause_mask, klause_value
from toolClasses import Combo2Relation
from TransKlauseEngine import TransKlauseEngine


def get_test_combos(r):
    ''' knames is a (string)sorted list, like [C001,C002,C003,..C038]
        return:[]
        '''
    lst = list(range(1, r + 1))
    L = len(lst)
    result = []
    while L > 0:
        result.append(lst[:])
        lst.pop(0)
        L = len(lst)
    return result


def get_root_dir():
    lst = os.getcwd().split('\\')
    index = lst.index("p3sat")
    lst1 = lst[:(index+1)]
    return '\\'.join(lst1)


def get_sdic(fname):  # fname is json-file name like *.json
    jfile = open(get_root_dir() + '\\test\\' + fname)
    da = jfile.read()
    sdic = eval(da)
    jfile.close()
    return sdic


def cut_kdic(kdic, finder_kname):
    kdic1 = {}                       # subset
    kns = sorted(list(kdic.keys()))  # super-set keys, sorted
    index = kns.index(finder_kname)
    if index < 0:
        raise("wrong finder-kname")
    sub_kns = kns[index:]

    for kn in sub_kns:
        kdic1[kn] = kdic[kn]
    return kdic1


def get_rel2(sdic, finder_kname, Tx=False):
    ''' when all knames (kns) are sorted by name, with the given finder_kname
        - index = kns.index(finder_kname), kns' = kns[(index+1):]
        - build a rel2 based on kns'
        '''
    nov = sdic['number_of_variables']
    kdic = sdic['kdic']        # super-set
    kdic1 = cut_kdic(kdic, finder_kname)

    # rel2 = Combo2Relation(kdic1, nov)
    if kdic != kdic1 and Tx:
        tx = TransKlauseEngine(kdic[finder_kname], nov)
        for kn in kdic1:
            kdic1[kn] = tx.trans_klause(kdic[kn])
    rel2 = Combo2Relation(kdic1, nov)
    return rel2


def get_kname(name, txname=None):
    ' turn (possibly number to kname '
    if type(name) == type(0) or name.isdigit():
        if txname:
            name = 'C' + txname + str(name).zfill(2)
        else:
            name = 'C' + str(name).zfill(3)
    return name


def merge_clauses(lst, rel2):
    ''' get merged super-clause(sc). If there existes conflict sc={}
        return: sc
        '''
    dic = {}
    mergeds = {}
    for name in lst:
        nam = get_kname(name)  # make sure it becomes string, not int
        dic1 = rel2.kdic[nam]
        if len(mergeds) == 0:
            dic = dic1.copy()
        else:
            for n, c in mergeds.items():
                ty = rel2.get_r2_type([nam, n])
                if ty.find('p') > -1:
                    return {}
                else:
                    for k, v in dic1.items():
                        if k not in dic:
                            dic[k] = v
        mergeds[nam] = dic1
    return dic


def _test_combination(klst, rel2):
    super_clause = merge_clauses(klst, rel2)
    L = len(super_clause)
    print(f'{super_clause} L:{L}')


def _test_maskvalue(klst, rel2):
    super_clause = merge_clauses(klst, rel2)
    if len(super_clause) > 0:
        mv = klause_mask(super_clause)
        print(f'super klause({klst})-mask-value: {mv}')
    else:
        print(f'no super-klause from {klst}')
    for k in klst:
        name = get_kname(k)
        klause = rel2.kdic[name]
        mv = klause_mask(klause)
        print(f'mask-value of {k}: {mv}')


def __manual_test(fname='./test/config1_result.json'):
    with open(fname) as jsfile:
        sdic = json.load(jsfile)
    rel2 = Combo2Relation(sdic['kdic'], sdic['number_of_variables'])

    while True:
        s = input("c)ombine | m)askvalue | e)nd: ")
        s = s.strip()
        if s == 'e':
            break
        elif s.startswith('c'):
            if len(s) == 1:
                msg = input("names for combination: ")
            else:
                msg = s[1:].strip()
            _test_combination(msg.split(), rel2)
        elif s == 'm':
            msg = input("names for mask-value calcs: ")
            _test_maskvalue(msg.split(), rel2)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        __manual_test()
    else:
        __manual_test(sys.argv[1])
    x = 1
