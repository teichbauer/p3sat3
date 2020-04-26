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


def trans_vkdic(vkd, seed_kn, top_bit, nov, top):
    tx = TransKlauseEngine(seed_kn, top_bit, vkd[seed_kn], nov, top)
    vkdic = {}
    for kn, vk in vkd.items():
        if kn == seed_kn:
            vkdic[kn] = VKlause(kn, tx.vklause.dic, nov)
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
                 top_bit,
                 base_vklause,  # inst of VKlause
                 nov,           # number of bits in value-space
                 top=True):     # transfer to top (0s) or bottom (1s)
        self.kname = kname
        self.start_vklause = base_vklause
        self.top_bit = top_bit
        self.nov = nov
        self.top = top
        self.name_txs = []   # list of exchange-tuple(pairs)
        self.value_txs = []  # list of post tx value-flip
        self.setup_tx_operators()

    def output(self):
        msg = self.kname + ': '+str(self.start_vklause.dic) + ', '
        msg += 'txn: ' + str(self.name_txs) + ', '
        msg += 'txv: ' + str(self.value_txs) + '\n'
        msg += '-'*60
        return msg

    def _find_tx_tuple(self, start_bit, lst=None):
        ''' find/return the tuple in self.name_txs, with given starting bit
            internal use only
            '''
        if lst == None:
            search_lst = self.name_txs
        else:
            search_lst = lst
        for t in search_lst:
            if t[0] == start_bit:
                return t
        if lst == None:  # use self.name_txs but not found? can't be
            raise(f"find_tx_tuple: ({start_bit},*) not in tuple-lst")
        return None

    def setup_tx_operators(self):

        # clone of vk.bits (they are in descending order from VKlause)
        bits = self.start_vklause.bits[:]
        if len(bits) == 0:
            return

        # target/left-most bits(names)
        L = len(bits)
        hi_bits = [self.nov - (i + 1) for i in range(L)]

        # be safe, in case top_bit was wrong, set it to be the highst in bits
        if len(bits) > 0 and not self.top_bit in bits:
            self.top_bit = bits[0]

        # manually setup transfer for self.top_bit to high-bit
        bits.remove(self.top_bit)
        h = hi_bits.pop(0)
        self.name_txs.append((h, self.top_bit))
        self.name_txs.append((self.top_bit, h))

        # setup transfers for the rest of the bits
        for b in bits:
            if b in hi_bits:
                hi_bits.remove(b)
                hi = b
            else:
                hi = hi_bits.pop(0)
                self.name_txs.append((hi, b))
                self.name_txs.append((b, hi))

        # now all bit:value pairs are in top/bottom positions
        # if any vlue in the pairs is 1 / 0,
        for b in self.start_vklause.dic:
            if self.start_vklause.dic[b] == int(self.top):
                txt = self._find_tx_tuple(b)
                post_tx_position = txt[1]
                self.value_txs.append(post_tx_position)

        # now tx the start_vklause to be self.vklause
        dic = {}
        hbits = [self.nov - (i + 1) for i in range(L)]
        for i in hbits:                  # top=True  -> bit-values: 0
            dic[i] = [1, 0][self.top]    # top=False -> bit-values: 1
        self.vklause = VKlause(self.kname, dic, self.nov)

    def trans_klause(self, klause):
        dic = {}
        ntxs = self.name_txs.copy()
        for b, v in klause.items():
            t = self._find_tx_tuple(b, ntxs)
            if t:
                ntxs.remove(t)  # drop t from ntxs
                new_bit = t[1]
                dic[new_bit] = v
            else:
                dic[b] = v
        for b, v in dic.items():
            if b in self.value_txs:
                dic[b] = int(not(v))
        return dic

    def trans_value(self, v):
        vdic = {}
        txn = self.name_txs.copy()
        for i in range(self.nov):
            bv = (v >> i) % 2  # i-th bit value
            t = self._find_tx_tuple(i, txn)
            if t:
                txn.remove(t)
                j = t[1]
                if j in self.value_txs:
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
        txn = self.name_txs.copy()
        for b, v in klause.items():
            if b in self.value_txs:
                nv = int(not v)
            else:
                nv = v
            t = self._find_tx_tuple(b, txn)
            if t:
                txn.remove(t)
                nb = t[1]
                dic[nb] = nv
            else:
                dic[b] = nv
        return dic

    def reverse_value(self, v):
        vdic = {}
        txn = self.name_txs.copy()
        for i in range(self.nov):
            bv = (v >> i) % 2
            if i in self.value_txs:
                bv = int(not bv)
            t = self._find_tx_tuple(i, txn)
            if t:
                txn.remove(t)
                j = t[1]
                vdic[j] = bv
            else:
                vdic[i] = bv
        newv = 0
        for b, v in vdic.items():
            if v == 1:
                newv |= (1 << b)
        return newv


def test_bitdic(conf_file_name):
    pass


if __name__ == '__main__':
    x = 0
    # --------------------
    test_dic()
    # --------------------
    x = 1
