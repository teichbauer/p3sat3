from vklause import VKlause

perf_count = {
    "SATS": [],
    "BitDic-init": 0,
    "TxTopKn": 0,
    "add_vklause": 0,
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


def check_finish(node):
    ''' criterion or criteria for being finished(dnoe, or sat):
        - when the seed vk is empty - it hits all value space
            which means, that no value left for being sat
            check_finish will set node.done = True
        - when nov == 1 (only 1 remaining variable), and
            the single bit's value 0 or 1 has no hit vk:
            this 0 ot 1, IS the sought sat value
        When sat found, return it. If not, node.done = False/True
        '''
    if node.nov == 3:
        return finish_nov3(node)
    rd = sorted(list(node.ordered_vkdic.keys()))
    if len(rd) > 1:
        kns = node.ordered_vkdic[rd[0]].copy()
        if 0 in node.ordered_vkdic:
            node.done = True
        elif 1 in node.ordered_vkdic:
            # check if there are 2 kn in kns, with
            # the same bit but opposite bit-values
            # E.G. bit-5:0 vs other bit-5:1)
            while not node.done and len(kns) >= 2:
                kn0 = kns.pop(0)
                k0 = node.vkdic[kn0].dic
                b0 = list(k0.keys())[0]
                for kn in kns:
                    k = node.vkdic[kn].dic
                    b = list(k.keys())[0]
                    if b0 == b and k0[b0] != k[b]:
                        node.done = True
                        break

        elif 2 in node.ordered_vkdic:
            pass
    return []
# ====== end of def check_finish(node)


def test4_finish(node):
    perf_count["test4_finish"] += 1
    sats = []
    sats = get_sats(node, check_finish(node))
    # sats = None
    if not node.done and node.nov == 1:
        if len(node.dic[0][0]) == 0:
            sats = get_sats(node, [0])
        if len(node.dic[0][1]) == 0:
            sats = get_sats(node, [1])
    return sats
# ==== end of def test4_finish(node)
