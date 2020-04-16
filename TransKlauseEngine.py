
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

            if self.start_klause[b] == 1:
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
