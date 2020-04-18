from visualizer import Visualizer
from vklause import VKlause

# test data with nov = 6
_kdic = {
    'C001': {5: 1, 4: 1, 3: 1},
    'C002': {2: 0, 1: 1, 0: 0},
    'C003': {5: 0, 4: 0, 2: 1}
}

test_dic = {
    'C1': {
        'C001': {5: 1, 4: 1, 3: 1},
        'C002': {2: 0, 1: 1, 0: 0},
        'C003': {5: 0, 4: 0, 2: 1}
    },
}


def make_vkdic(kdic, nov):
    vkdic = {}
    for kn, klause in kdic.items():
        vkdic[kn] = VKlause(kn, klause, nov)
    return vkdic


def trans_vkdic(vkd, seed_kn, nov, top):
    tx = TransKlauseEngine(seed_kn, vkd[seed_kn], nov, top)
    vkdic = {}
    for kn, vk in vkd.items():
        if kn == seed_kn:
            vkdic[kn] = VKlause(kn, tx.klause, nov)
        else:
            vkdic[kn] = VKlause(kn, tx.trans_klause(vk.dic), nov)
    return vkdic, tx


class TransKlauseEngine:
    """ move base_klause's bits to the left-most positions, and
        set them to be 0s or 1s (depending on top), assign to self.klause. 
        while doing this, set up operators so that any klause 
        will be transfered to a new klause compatible to self.klause
        """

    def __init__(self,
                 kname,         # name of the klause
                 base_vklause,  # inst of VKlause
                 nov,           # number of bits in value-space
                 top=True):     # transfer to top (0s) or bottom (1s)
        self.kname = kname
        self.start_vklause = base_vklause
        self.nov = nov
        self.top = top
        self.setup_tx_operators()

    def output(self):
        msg = self.kname + ': '+str(self.start_vklause.dic) + ', '
        msg += 'txn: ' + str(self.bitname_tx) + ', '
        msg += 'txv: ' + str(self.bitvalue_tx) + '\n'
        msg += '-'*60
        return msg

    def setup_tx_operators(self):
        bits = self.start_vklause.bits[:]
        L = len(bits)
        # target/left-most 3 bits(names)
        hi_bits = [self.nov - (i + 1) for i in range(L)]
        self.bitname_tx = {}
        self.bitvalue_tx = {}
        bits.reverse()        # order: higher-bit -> lower-bit
        for b in bits:
            if b in hi_bits:
                hi_bits.remove(b)
                hi = b
            else:
                hi = hi_bits.pop(0)
                self.bitname_tx[b] = hi
                self.bitname_tx[hi] = b

            if self.start_vklause.dic[b] == int(self.top):
                self.bitvalue_tx[hi] = True
        self.klause = {}
        hbits = [self.nov - (i + 1) for i in range(L)]
        for i in hbits:                      # top=True  -> bit-values: 0
            self.klause[i] = [1, 0][self.top]  # top=False -> bit-values: 1

    def trans_klause(self, klause):
        dic = {}
        txn = self.bitname_tx.copy()
        for b, v in klause.items():
            if b in txn:
                new_bit = txn.pop(b)
                dic[new_bit] = v
            else:
                dic[b] = v
        for b, v in dic.items():
            if b in self.bitvalue_tx:
                dic[b] = int(not(v))
            else:
                dic[b] = v
        return dic

    def trans_value(self, v):
        vdic = {}
        txn = self.bitname_tx.copy()
        vxs = list(self.bitvalue_tx.keys())
        for i in range(self.nov):
            bv = (v >> i) % 2  # i-th bit value
            if i in txn:
                j = txn.pop(i)
                if j in vxs:
                    vdic[j] = int(not bv)
                else:
                    vdic[j] = bv
            else:
                vdic[i] = bv
        newv = 0
        for b, v in vdic.items():
            if v == 1:
                newv |= (1 << b)
        return newv

    def reverse_klause(self, klause):
        dic = {}
        txn = self.bitname_tx.copy()
        vxs = list(self.bitvalue_tx.keys())
        for b, v in klause.items():
            if b in vxs:
                nv = int(not v)
            else:
                nv = v
            if b in txn:
                nb = txn.pop(b)
                dic[nb] = nv
            else:
                dic[b] = nv
        return dic

    def reverse_value(self, v):
        vdic = {}
        txn = self.bitname_tx.copy()
        vxs = list(self.bitvalue_tx.keys())
        for i in range(self.nov):
            bv = (v >> i) % 2
            if i in vxs:
                bv = int(not bv)
            if i in txn:
                j = txn.pop(i)
                vdic[j] = bv
            else:
                vdic[i] = bv
        newv = 0
        for b, v in vdic.items():
            if v == 1:
                newv |= (1 << b)
        return newv


def test(filename, seed, top):
    vkd = make_vkdic(_kdic, 8)

    new_vkd, tx = trans_vkdic(vkd, seed, 8, top)
    vis = Visualizer(new_vkd, 8)
    vis.output(filename, tx)
    '''
    if seed == 'C001':
        vis = Visualizer(vkd, 6)
        vis.output(filename)
    else:
        new_vkd = trans_vkdic(vkd, seed, top)
        vis = Visualizer(new_vkd, 6)
        vis.output(filename)
    '''


def test_bitdic(conf_file_name):
    pass


if __name__ == '__main__':
    x = 0
    # --------------------
    test_dic()
    # --------------------
    # top = True
    # test('test-C001-top.txt', 'C001', top)
    # test('test-C002-top.txt', 'C002', top)
    # test('test-C003-top.txt', 'C003', top)

    # top = False
    # test('test-C003.txt', 'C003', top)
    # test('test-C002.txt', 'C002', top)
    # test('test-C001.txt', 'C001', top)
    # --------------------
    x = 1
