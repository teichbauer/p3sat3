
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

# ============================================


def get_bit(val, bit):
    return (val >> bit) & 1


def set_bit(val, bit_index, new_bit_value):
    """ Set the bit_index (0-based) bit of val to x (1 or 0)
        and return the new val.
        """
    mask = 1 << bit_index  # mask - integer with just hte chosen bit set.
    val &= ~mask           # Clear the bit indicated by the mask (if x == 0)
    if new_bit_value:
        val |= mask        # If x was True, set the bit indicated by the mask.
    return val             # Return the result, we're done.


def flip_bit(val, bit):
    v0 = get_bit(val, bit)
    v1 = set_bit(val, bit, int(not v0))
    return v1


def trade_bits(val, bit_tuple):
    v1 = get_bit(val, bit_tuple[0])         # read bit-1 -> v1 (0 or 1)
    v2 = get_bit(val, bit_tuple[1])         # read bit-2 -> v2 (0 or 1)
    val1 = set_bit(val,  bit_tuple[1], v1)  # set v1 (0 or 1), to bit-2
    val2 = set_bit(val1, bit_tuple[0], v2)  # set v2 (0 or 1), to bit-1
    return val2


def trade_lst_elements(lst, pos_tuple):
    lst1 = lst[:]
    p0, p1 = pos_tuple
    lst1[p0] = lst[p1]
    lst1[p1] = lst[p0]
    return lst1


# =================================================


def get_sats(start_node, vs):
    node = start_node
    nvs = vs[:]
    # with vkdic empty, there is only 1 line of value, the search of v
    # is just one single line, starting with 0. so v = 0
    while node:
        if node.conversion == None:  # reached root-seed
            break
        if type(node.conversion) == type(''):
            splt = node.conversion.split("'")
            shift, bitvalue = int(splt[0]), int(splt[1])
            if bitvalue == 1:
                nvs = [v + (1 << shift) for v in nvs]
        else:
            tx = node.conversion
            nvs = [tx.reverse_value(v) for v in nvs]
        node = node.parent
    return nvs
