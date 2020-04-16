class VKlause:
    ''' veriable klause - klause with 1, 2 or 3 bits.
        nov is the value-space bit-count, or number-of-variables
        bits is a list of bits in ascending order
        '''

    def __init__(self, kname, dic, nov):
        self.kname = kname
        self.dic = dic          # { 7:1, 3: 0, 0: 1}, or {3:0, 1:1} or {3:1}
        self.nov = nov          # number of variables - bits of value space
        self.bits = sorted(list(dic.keys()))  # can be of length: 1,2,3
        self.nob = len(self.bits)             # 1, 2 or 3
        self.tailsize = self.bits[0]          # gap btwn low bit and 0
        self.set_filter_and_mask()

    def set_filter_and_mask(self):
        ''' For the example klause {7:1, 5:0, 2:1}
                              BITS:   7  6  5  4  3  2  1  0
            the relevant bits:        *     *        *
            {7:1, 5:0, 2:1}'s filter: 1  0  1  0  0  1  0  0
            surppose v = 135 bin(v):  1  0  0  0  0  1  1  1
            x = v AND filter =        1  0  0  0  0  1  0  0
            bits of v left(rest->0):  ^     ^        ^
            {7:1, 5:0, 2:1}' mask  :  1  0  0  0  0  1  0  0
            This methos set self.filter
            '''
        filter = 0
        mask = 0
        for k, v in self.dic.items():
            filter = filter | (1 << k)
            if v == 1:
                mask = mask | (1 << k)
        self.mask = mask
        self.filter = filter

    def value(self):
        return self.mask

    def position_value(self):
        ''' regardless v be 0 or 1, set the bit 1
            For I am caring only the position of the bits  '''
        return self.filter

    def hit(self, v):  # hit means here: v let this klause turn False
        fv = self.filter & v
        return not bool(self.mask ^ fv)
