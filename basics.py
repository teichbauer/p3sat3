
def klause_value(klause):
    # regardless v be 0 or 1, set the bit 1
    # For I am caring only the position of the bits
    r = 0
    for b, v in klause.items():
        if v == 1:
            r = r | 1 << b
    return r


def klause_mask(klause):
    '''
    klause can be union of multiple klauses, namely a super-klause
    '''
    v = 0
    for b in klause:
        x = 1 << b
        v = v | x
    return v


def get_setlst(order, cdic):  # Complexity for order == 2: O(m**2)
    ''' setlst_dic = {}  # {2: [{'C001','C002'},...], 3:[], ...}
        -------------------------------------------------------------
        fill a list in setlst_dic[order]. E.G. for order == 2
        setlst_dic[2] will have [{'C001','C002'},...] and return this list
        ----------------------------
        '''
    base = sorted(list(cdic.keys()))
    setlst_dic = {}  # {2: [{'C001','C002'},...], 3:[], ...}
    if order not in setlst_dic:
        slst = setlst_dic.setdefault(order, [])
        if order == 2:
            return fill_2set(base[:], slst)
        else:
            if (order - 1) not in setlst_dic:
                last_lst = get_setlst(order - 1, cdic)
            else:
                last_lst = setlst_dic[order - 1]
            for s in last_lst:
                for b in base:
                    if b not in s:
                        ss = s.copy()
                        ss.add(b)
                        if ss not in slst:
                            slst.append(ss)
    return setlst_dic[order]


def fill_2set(src, lst2):  # Complexity: O(m**2)
    ''' used in get_setlst, for case order==2
        src is a mutable list. should be a copy, to prevent side-effect
        '''
    if len(src) < 2:
        return lst2
    k1 = src.pop(0)
    for k in src:
        kpair = [k1, k]
        kset = set(kpair)
        if kset not in lst2:
            lst2.append(kset)
    return fill_2set(src, lst2)

# find out how many SATs / UNSATs values, for a given
#  test_set, looking like {'C001','C002'} or {'C004','C010','C012'}


# def combine(test_set, vdic, output=True):
#     sats = []
#     unsats = []
#     for v in vdic:
#         if vdic[v]:
#             if len(vdic[v]) == 0:
#                 # if no blocker exists (vdic[v] == None) -> SAT
#                 sats.append(v)
#             else:
#                 if vdic[v].isdisjoint(test_set):
#                     # if test-set and set from vdic[v] are is-joint -> SAT
#                     sats.append(v)
#                 else:
#                     # test-set and set from vdic[v] interset -> UNSAT
#                     unsats.append(v)
#         else:
#             # if no blocker exists (vdic[v] == None) -> SAT
#             sats.append(v)
#     if output:
#         out_to_files(test_set, unsat, sat)


# def out_to_files(testSet, unsat, sat):
#     dirname = str(len(test_set))
#     fname = '-'.join(test_set) + '.txt'
#     f = open(f'./combinations/{dirname}/{fname}', 'w')
#     f.write(fname + '\n')
#     f.write('no of SATS:' + str(len(sats)) + '\n')
#     f.write('no of UNSATS:' + str(len(unsats)) + '\n')
#     f.write('='*80 + '\n')
#     f.write('SATs: \n' + str(sats))
#     f.write('-'*80 + '\n')
#     f.write('UNSATs: \n' + str(unsats))
#     f.close()
