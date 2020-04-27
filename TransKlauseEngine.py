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


def get_bit(val, bit):
    return (val >> bit) & 1


def construct_value_from_dict(d):
    value = 0
    for b, v in d.items():
        if v == 1:
            value |= (1 << b)
    return value


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

    def _find_tx_tuple(self, head_or_tail, bit, lst=None):
        ''' find/return the tuple in self.name_txs, with given starting bit
            internal use only
            '''
        # index = (0,1) for head_or_tail = (True, False)
        index = int(not head_or_tail)

        if lst == None:
            search_lst = self.name_txs
        else:
            search_lst = lst
        for t in search_lst:
            if t[index] == bit:
                return t
        if lst == None:  # use self.name_txs but not found? can't be
            raise(f"find_tx_tuple: ({bit},*) not in tuple-lst")
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
        # self.name_txs.append((h, self.top_bit))
        self.name_txs.append((self.top_bit, h))

        # setup transfers for the rest of the bits
        for b in bits:
            if b in hi_bits:
                hi_bits.remove(b)
                hi = b
            else:
                hi = hi_bits.pop(0)
                # self.name_txs.append((hi, b))
                self.name_txs.append((b, hi))

        # now all bit:value pairs are in top/bottom positions
        # if any vlue in the pairs is 1 / 0,
        for b in self.start_vklause.dic:
            if self.start_vklause.dic[b] == int(self.top):
                txt = self._find_tx_tuple(True, b)  # head: True
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
        bs = list(klause.keys())
        while len(bs) > 0:
            b = bs.pop(0)
            t = self._find_tx_tuple(True, b, ntxs)  # head: True
            if t:
                ntxs.remove(t)  # drop t from ntxs
                t0, t1 = t      # destruct t into t0, t1, b == t0
                dic[t1] = klause[b]
                # the reverse side of the exchange
                if t1 in klause:
                    dic[b] = klause[t1]
            else:
                dic[b] = klause[b]

        for b, v in dic.items():
            if b in self.value_txs:
                dic[b] = int(not(v))
        return dic

    def trans_value(self, v):
        vdic = {}
        txn = self.name_txs.copy()
        for i in range(self.nov):
            bv = get_bit(v, i)  # i-th bit value in v
            t = self._find_tx_tuple(True, i, txn)   # head: True
            if t:
                txn.remove(t)   # drop t from txn
                t0, t1 = t      # t[0] == i
                if t1 in self.value_txs:
                    vdic[t1] = int(not bv)
                else:
                    vdic[t1] = bv
                # the reverse side of the exchange
                nv = get_bit(v, t1)
                if i in self.value_txs:
                    vdic[i] = int(not nv)
                else:
                    vdic[i] = nv
            else:
                vdic[i] = bv
        return construct_value_from_dict(vdic)

    def reverse_klause(self, klause):
        dic = {}
        txn = self.name_txs.copy()
        bs = list(klause.keys())
        while len(bs) > 0:
            b = bs.pop(0)
            if b in self.value_txs:
                nv = int(not klause[b])
            else:
                nv = klause[b]
            t = self._find_tx_tuple(False, b, txn)  # head: False, find tail
            if t:
                txn.remove(t)
                t0, t1 = t  # destruct t, b == t1
                dic[t0] = nv
                # the reverse side of the exchange
                if t0 in bs:
                    bs.remove(t0)
                    if t0 in self.value_txs:
                        dic[t1] = int(not klause[t0])
                    else:
                        dic[t1] = klause[t0]
            else:
                dic[b] = nv
        return dic

    def reverse_value(self, v):
        vdic = {}
        txn = self.name_txs.copy()
        for i in range(self.nov):
            bv = get_bit(v, i)
            if i in self.value_txs:
                bv = int(not bv)
            t = self._find_tx_tuple(False, i, txn)  # head:False, find tail==i
            if t:
                t0, t1 = t      # destruct t into t0 t1, t1 == i
                txn.remove(t)
                vdic[t0] = bv
                # the reverse side of the exchange
                bv = get_bit(v, t0)
                if t0 in self.value_txs:
                    bv = int(not t0)
                vdic[t1] = bv
            else:
                vdic[i] = bv
        return construct_value_from_dict(vdic)


def test_bitdic(conf_file_name):
    pass


if __name__ == '__main__':
    # --------------------
    test_dic()
    # --------------------
    x = 1
