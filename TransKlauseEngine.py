class TransKlauseEngine:
    """
    move base_klause's 3 bits to the left-most positions, and
    set them to be 0 0 0 -> self.klause. while doing this, set up 
    operators so that any klause (coming from base_klause's set) 
    will be trnasfered to a new klause compatible to self.klause
    """

    def __init__(self, base_klause, nov):
        self.start_klause = base_klause
        self.nov = nov
        self.setup_tx_operators()

    def setup_tx_operators(self):
        bits = sorted(list(self.start_klause.keys()))
        bits.reverse()
        # target/left-most 3 bits(names)
        hi_bits = [self.nov - 1, self.nov - 2, self.nov - 3]
        self.bitname_tx = {}
        self.bitvalue_tx = {}
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
        n = self.nov - 1
        self.klause = {n: 0, n-1: 0, n-2: 0}

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
