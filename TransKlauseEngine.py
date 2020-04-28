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


def trade_bits(val, bit_tuple):  # bit1, bit2):
    v1 = get_bit(val, bit_tuple[0])         # read bit-1 -> v1 (0 or 1)
    v2 = get_bit(val, bit_tuple[1])         # read bit-2 -> v2 (0 or 1)
    val1 = set_bit(val,  bit_tuple[1], v1)  # set v1 (0 or 1), to bit-2
    val2 = set_bit(val1, bit_tuple[0], v2)  # set v2 (0 or 1), to bit-1
    return val2


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


# def trans_vkdic(vkd, seed_kn, top_bit, nov, top):
#     tx = TransKlauseEngine(seed_kn, top_bit, vkd[seed_kn], nov, top)
#     vkdic = {}
#     for kn, vk in vkd.items():
#         if kn == seed_kn:
#             vkdic[kn] = VKlause(kn, tx.vklause.dic, nov)
#         else:
#             vkdic[kn] = VKlause(kn, tx.trans_klause(vk.dic), nov)
#     return vkdic, tx


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

    def trans_klause(self, vklause):
        klause = vklause.dic
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
                if t1 in bs:
                    bs.remove(t1)
                    dic[t0] = klause[t1]
            else:
                t = self._find_tx_tuple(False, b, ntxs)  # head: False
                if t:
                    ntxs.remove(t)  # drop t from ntxs
                    t0, t1 = t      # destruct t into t0, t1, b == t1
                    dic[t0] = klause[t1]
                    if t0 in bs:
                        bs.remove(t0)
                        dic[t1] = klause[t0]
                else:
                    dic[b] = klause[b]

        for b, v in dic.items():
            if b in self.value_txs:
                dic[b] = int(not(v))
        return VKlause(self.kname, dic, self.nov)

    def trans_value(self, v):
        new_v = v
        for t in self.name_txs:
            new_v = trade_bits(new_v, t)

        for b in self.value_txs:
            new_v = flip_bit(new_v, b)
        return new_v

    def trans_klauses(self, vkdic):
        vdic = {}
        for kn, vk in vkdic.items():
            if kn == self.kname:
                vdic[kn] = self.vklause
            else:
                vdic[kn] = self.trans_klause(vk)
        return vdic

    def reverse_value(self, v):
        new_v = v
        for b in self.value_txs:
            new_v = flip_bit(new_v, b)

        lst = self.name_txs[:]
        lst.reverse()
        for t in lst:
            new_v = trade_bits(new_v, t)
        return new_v

    def reverse_values(self, vs):
        res = []
        for v in vs:
            res.append(self.reverse_value(v))
        return res

    def trans_values(self, vs):
        res = []
        for v in vs:
            res.append(self.trans_value(v))
        return res

    # def trans_value(self, v):
    #     new_v = v
    #     txn = self.name_txs.copy()
    #     from_pos = [i for i in range(self.nov)]
    #     to_pos = from_pos[:]

    #     while len(txn) > 0:
    #         t = txn.pop(0)
    #         t0, t1 = t
    #         from_pos.remove(t0)
    #         to_pos.remove(t1)
    #         set_bit(new_v, t1, get_bit(v, t0)
    #         chain_t=self._find_tx_tuple(True, t1, txn)
    #         if not chain_t:
    #             from_pos.remove(t1)
    #             to_posremove(t0)
    #             set_bit(new_v, t0, get_bit(v, t1))

    #     i=0
    #     while i < len(from_pos):
    #         if from_pos[i] in to_pos:
    #             from_pos.remove(i)
    #             to_pos.remove(i)
    #             set_bit(new_v, i, get_bit(v, i))
    #         else:
    #             i += 1
    #     if len(from_pos) > 0:
    #         fbit=from_pos.pop(0)
    #         tbit=to_pos.pop(0)
    #         set_bit(new_v, tbit, get_bit(, fbit))
    #         if len(from_pos) > 0 or len(to_pos) > 0:
    #             raise("weirdo")


def test_bitdic(conf_file_name):
    pass


if __name__ == '__main__':
    # --------------------
    test_dic()
    # --------------------
    x = 1
