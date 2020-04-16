
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


def get_sdic(filename):
    sdic = eval(open(filename).read())
    return sdic
