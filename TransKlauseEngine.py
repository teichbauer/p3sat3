from visualizer import Visualizer
from vklause import VKlause
from basics import get_bit, set_bit, flip_bit, trade_bits, trade_lst_elements


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
        self.setup_tx()

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
            lst = self.name_txs

        for t in lst:
            if t[index] == bit:
                return t
        if lst == None:  # use self.name_txs but not found? can't be
            raise(f"find_tx_tuple: ({bit},*) not in tuple-lst")
        return None

    def setup_tx(self):
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
            if b in hi_bits:       # b already in high-pos, no transfer
                hi_bits.remove(b)  # of bit needed - for this bit
            else:
                hi = hi_bits.pop(0)
                # self.name_txs.append((hi, b))
                self.name_txs.append((b, hi))

        # now all bit:value pairs are in top/bottom positions
        # they must all be 0 (self.top: True) or 1 (self.top: False)
        for b in self.start_vklause.dic:
            if self.start_vklause.dic[b] == int(self.top):  # 1
                t = self._find_tx_tuple(True, b)  # head: True
                if t:
                    post_tx_position = t[1]
                    self.value_txs.append(post_tx_position)
                else:  # b not in any bit-tx, it remains in right position
                    self.value_txs.append(b)  # but b's value needs flip

        # now tx the start_vklause to be self.vklause
        dic = {}
        hbits = [self.nov - (i + 1) for i in range(L)]
        for i in hbits:                  # top=True  -> bit-values: 0
            dic[i] = [1, 0][self.top]    # top=False -> bit-values: 1
        self.vklause = VKlause(self.kname, dic, self.nov)

    def trans_klause(self, vklause):
        klause = vklause.dic.copy()
        bs = list(klause.keys())
        lst = []
        for i in range(self.nov):
            if i in bs:
                lst.append(klause[i])
            else:
                lst.append(None)
        for t in self.name_txs:
            lst = trade_lst_elements(lst, t)
        for flip in self.value_txs:
            if lst[flip] != None:
                lst[flip] = int(not lst[flip])
        dic = {}
        for i, e in enumerate(lst):
            if e != None:
                dic[i] = e
        return VKlause(vklause.kname, dic, self.nov)

    def trans_value(self, v):
        new_v = v
        for t in self.name_txs:
            new_v = trade_bits(new_v, t)

        for b in self.value_txs:
            new_v = flip_bit(new_v, b)
        return new_v

    def trans_vkdic(self, vkdic):
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

    def test_me(self, vkdic):
        kns = sorted(list(vkdic.keys()))
        nvkdic = self.trans_vkdic(vkdic)

        vdic = {}
        vhit_dic = {}
        N = 2 ** self.nov
        for v in range(N):
            nv = self.trans_value(v)

            hset0 = set([])
            for kn, vk in vkdic.items():
                if vk.hit(v):
                    hset0.add(kn)

            hset = set([])
            for kn, vk in nvkdic.items():
                if vk.hit(nv):
                    hset.add(kn)

            if hset0 != hset:
                debug = 1
                print(f'Tx test failed on: {v}')
                return False
        return True


if __name__ == '__main__':
    x = 1
