from visualizer import Visualizer
from vklause import VKlause

# test data with nov = 6
_kdic = {
    'C001': {5: 1, 4: 1, 3: 1},
    'C002': {2: 0, 1: 1, 0: 0},
    'C003': {5: 0, 4: 0, 2: 1}
}


def make_vkdic(kdic):
    vkdic = {}
    for kn, klause in kdic.items():
        vkdic[kn] = VKlause(kn, klause, 6)
    return vkdic


def trans_vkdic(vkd, seed_kn):
    tx = TransKlauseEngine(vkd[seed_kn], 6, False)
    vkdic = {}
    for kn, vk in vkd.items():
        vkdic[kn] = VKlause(kn, tx.trans_klause(vk.dic), 6)
    return vkdic


class TransKlauseEngine:
    """ move base_klause's bits to the left-most positions, and
        set them to be 0s or 1s (depending on top), assign to self.klause. 
        while doing this, set up operators so that any klause 
        will be transfered to a new klause compatible to self.klause
        """

    def __init__(self,
                 base_vklause,  # inst of VKlause
                 nov,           # number of bits in value-space
                 top=True):     # transfer to top (0s) or bottom (1s)
        self.start_vklause = base_vklause
        self.nov = nov
        self.setup_tx_operators()
        self.top = top

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

            if self.start_vklause.dic[b] == 1:
                self.bitvalue_tx[hi] = True
        self.klause = {}
        for i in hi_bits:                      # top=True  -> bit-values: 0
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
            if i in tnx:
                j = nx.pop(i)
                vdic[j] = bv
            else:
                vdic[i] = bv
        newv = 0
        for b, v in vdic.items():
            if v == 1:
                newv |= (1 << b)
        return newv


def test(filename, seed):
    vkd = make_vkdic(_kdic)
    if seed == 'C001':
        vis = Visualizer(vkd, 6)
        vis.output(filename)
    else:
        new_vkd = trans_vkdic(vkd, 'C002')
        vis = Visualizer(new_vkd, 6)
        vis.output(filename)


if __name__ == '__main__':
    x = 0
    test('test-C001.txt', 'C001')
    x = 1
