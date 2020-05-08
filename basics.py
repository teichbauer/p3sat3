from vklause import VKlause

perf_count = {
    "SATS": [],
    "BitDic-init": 0,
    "TxTopKn": 0,
    "add_clause": 0,
    "set_txseed": 0,
    "test4_finish": 0,
    "time-used":    0.0,
    "split_topbit": 0
}


def get_sdic(filename):
    sdic = eval(open(filename).read())
    return sdic


def make_vkdic(kdic, nov):
    vkdic = {}
    for kn, klause in kdic.items():
        vkdic[kn] = VKlause(kn, klause, nov)
    return vkdic

# ============================================


def finish_nov3(bitdic):
    ''' when bitdic.nov == 3, the value-space is 8
        check if the vklauses in bitdic.vkdic cover all of them
        '''
    sats = []
    if bitdic.nov == 3:
        unhits = bitdic.check8set.copy()
        for kn, vk in bitdic.vkdic.items():
            if len(unhits) == 0:
                return []
            if vk.nob == 0:
                bitdic.done = True
                return []
            unhits = unhits - set(vk.hit_values_nov3())
        sats = list(unhits)
    return sats


def get_sats(start_node, vs):
    nos = len(vs)
    if nos == 0:
        return []
    print(f'{nos} sat(s) found!!!')
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
