from basics import get_sdic
from vklause import VKlause
from visualizer import Visualizer
from TransKlauseEngine import make_vkdic, TransKlauseEngine

perf_count = {
    "BitDic-init": 0,
    "TxTopKn": 0,
    "add_clause": 0,
    "set_txseed": 0,
    "test4_finish": 0,
    "time-used":    0.0,
    "split_topbit": 0
}


class BitDic:
    ''' maintain a bit-dict:
        self.dic: { 7:[ [C1,C6], -- 7-th bit, these Clauses have it be 0
                        []       -- 7-th bit, these Clauses have it be 1
                      ],
                    6: [[],[]],
                ...
        }
        self.dic[7][0] -> [<list of clause-names, that use this bit, value:0>]
        self.dic[7][1] -> [<list of clause-names, that use this bit, value:1>]
        '''

    def __init__(self, seed_name, bdname, vkdic, nov):   # O(m)
        perf_count["BitDic-init"] += 1
        self.seed_name = seed_name
        self.name = bdname
        self.nov = nov
        self.dic = {}   # keyed by bits, value: [[0-kns],[1-kns]]
        self.vkdic = vkdic
        self.parent = None  # the parent that generated / tx-to self
        self.done = False
        self.ordered_vkdic = {}
        for i in range(nov):        # number_of_variables from config
            self.dic[i] = [[], []]
        self.add_clause()
        self.conversion = None
        self.vis = Visualizer(self.vkdic, self.nov)

    def split_topbit(self, debug=False):
        ''' if self.nov = 8, top bit is bit-7.
            now bit-7 will be dropped, and self be split into
            2 bitdic:
            - bitdic0     -- all vks with bit-7 == 0. no Tx.
            - bitdic_tmp  -- all vks with bit-7 == 1. Tx to
                bitdic1 with seed picked from bitdic_tmp's vks
            if bitdic0 or bitdic_tmp has sat, return <sat>, None
            else, return bitdic0, bitdic1
            '''
        perf_count["split_topbit"] += 1
        tb = self.nov - 1   # top bit number
        vkdic0 = {}     # vks with top-bit == 0
        vkdic1 = {}     # vks with top-bit == 1
        vkdic_mix = {}  # vks with top-bit not used

        kns = list(self.vkdic.keys())

        for kn in self.dic[tb][0]:
            vklause = self.vkdic[kn]
            # drop top bit, nov decrease by 1 (tp)
            # vklause.dic.pop(tb, None)
            vklause.drop_bit(tb)
            vkdic0[kn] = VKlause(kn, vklause.dic, tb)

        for kn in self.dic[tb][1]:
            vklause = self.vkdic[kn]
            # drop top bit, nov decrease by 1 (tp)
            # vklause.dic.pop(tb, None)
            vklause.drop_bit(tb)
            vkdic1[kn] = VKlause(kn, vklause.dic, tb)

        for kn in kns:
            if (kn not in vkdic0) and (kn not in vkdic1):
                vklause = self.vkdic[kn]
                # no need to drop top bit, they don't have it.
                vkdic_mix[kn] = VKlause(kn, vklause.dic, tb)

        vkdic0.update(vkdic_mix)  # add mix-dic to 0-dic
        vkdic1.update(vkdic_mix)  # add mix-dic to 1-dic

        bitdic0 = BitDic(
            self.seed_name,
            self.name + f'-{tb}@0',
            vkdic0,
            tb)

        # from self to bitdic0: bit<tb> with value 0 droped
        # when converting back, a 0 should be added on tb-bit
        bitdic0.conversion = f'{tb}@0'
        bitdic0.parent = self

        sat = bitdic0.test4_finish()
        if sat != None:
            return sat, None

        bdic = self.dic.copy()  # clone the bit-dic from self
        bdic.pop(tb)            # drop the top bit in bdic
        seed, top_bit = self.set_txseed(vkdic1, bdic)
        if seed == None:
            # with vkdic empty, there is only 1 line of value,
            # the search of v is just one single line, starting with 0.
            # so v = 0
            return self.get_sat(0), None
        else:
            bitdic_tmp = BitDic(
                f'~{self.seed_name}',
                self.name + f'-{tb}@1',
                vkdic1,
                tb)
            # from self to bitdic_tmp: bit<tb> with value 1 droped
            # when converting back, a 1 should be added on tb-bit
            bitdic_tmp.conversion = f'{tb}@1'
            bitdic_tmp.parent = self

            # the 2 returning bitdics will be visualized in solver4
            # here is for visualize the tmp
            if debug:
                bitdic_tmp.visualize()

            sat = bitdic_tmp.test4_finish()
            if sat != None:
                return sat, None

            if not bitdic_tmp.done:
                # bitdic1 be tx-ed on 1 of its shortkns
                bitdic1 = bitdic_tmp.TxTopKn(seed, top_bit)
                # print(f'for bitdic1t Tx-seed:{seed}')
            else:
                bitdic1 = bitdic_tmp
            return bitdic0, bitdic1

    def get_sat(self, v):
        node = self
        # with vkdic empty, there is only 1 line of value, the search of v
        # is just one single line, starting with 0. so v = 0
        while node:
            if node.conversion == None:  # reached root-seed
                break
            if type(node.conversion) == type(''):
                splt = node.conversion.split('@')
                shift, bitvalue = int(splt[0]), int(splt[1])
                if bitvalue == 1:
                    v = v + (1 << shift)
            else:
                tx = node.conversion
                v = tx.reverse_value(v)
            node = node.parent
        return v

    def check_finish(self):
        rd = sorted(list(self.ordered_vkdic.keys()))
        if len(rd) > 1:
            kns = self.ordered_vkdic[rd[0]].copy()
            if 0 in self.ordered_vkdic:
                self.done = True
            elif 1 in self.ordered_vkdic:
                # check if there are 2 kn in kns, with
                # the same bit but opposite bit-values
                # E.G. bit-5:0 vs other bit-5:1)
                while not self.done and len(kns) >= 2:
                    kn0 = kns.pop(0)
                    k0 = self.vkdic[kn0].dic
                    b0 = list(k0.keys())[0]
                    for kn in kns:
                        k = self.vkdic[kn].dic
                        b = list(k.keys())[0]
                        if b0 == b and k0[b0] != k[b]:
                            self.done = True
                            break

            elif 2 in self.ordered_vkdic:
                pass

    def test4_finish(self):
        ''' criterion or criteria for being finished(dnoe, or sat):
            - when the seed vk is empty - it hits all value space
              which means, that no value left for being sat
              this will set self.done = True
            - when nov == 1 (only 1 remaining variable), and
              the single bit's value 0 or 1 has no hit vk:
              this 0 ot 1, IS the sought sat value
            When sat found, return it. If not, self.done = False/True
            '''
        perf_count["test4_finish"] += 1
        self.check_finish()
        sat = None
        if not self.done and self.nov == 1:
            if len(self.dic[0][0]) == 0:
                sat = self.get_sat(0)
            if len(self.dic[0][1]) == 0:
                sat = self.get_sat(1)
        return sat

    def most_popular(self, d):
        ''' Among every bit of d[bit] = [[0-kns],[10kns]]
            find which bit has the most sum: len([0-kns]) + len([1-kns])
            This is used as the power of this bit (how popular)
            make a dict keyed by power, value is bit-number
            return all kns(from both 0/1 bit-values) of 
            the most power-full, of most popular bit
            '''
        bit_powers = {}  # <power>:<bit-name>}
        for b in d:
            bit_powers[len(d[b][0]) + len(d[b][1])] = b
        ps = sorted(list(bit_powers.keys()), reverse=True)
        # all knames in both 0-kns and 1-kns
        best_bit = bit_powers[ps[0]]
        kns = d[best_bit][0] + d[best_bit][1]
        return set(kns), best_bit

    def set_txseed(self, vkdic=None, bdic=None):
        ''' pick/return a kn as seed, in vkdic with shortest dic, and
            also popular
            '''
        perf_count["set_txseed"] += 1
        initial = vkdic == None
        if initial:
            lst = list(self.vkdic.keys())
            bdic = self.dic
        else:
            L = 4     # bigger than any klause length, so it will bereplaced
            lst = []  # list of kns with the same shortest length
            for kn in vkdic:
                if vkdic[kn].nob <= L:
                    L = vkdic[kn].nob
                    # remove kns in lst with length > L
                    i = 0
                    while i < len(lst):
                        if self.vkdic[lst[i]].nob > L:
                            lst.pop(i)
                        else:
                            i += 1
                    lst.append(kn)
        if len(lst) == 0:
            x = 1
            return None
        popular_kns, top_bit = self.most_popular(bdic)
        for kn in lst:
            if kn in popular_kns:
                return kn, top_bit
        return lst[0], top_bit

    def TxTopKn(self, tx_seed, top_bit):
        perf_count["TxTopKn"] += 1
        tx = TransKlauseEngine(
            tx_seed,                # tx.name
            top_bit,                # this bit will be most sig bit
            self.vkdic[tx_seed],    # start-klause
            self.nov,
            True)                   # trans to the top-position (v == 0)

        new_vkdic = tx.trans_klauses(self.vkdic)

        # new_vkdic, tx = trans_vkdic(
        #     self.vkdic,     # tx all vkdic members
        #     tx_seed,        # seed-kn for Tx
        #     top_bit,        # this bit from seed-klause will turn to top-bit
        #     self.nov,       # nov remains the same
        #     True)           # Tx-to-top-position: True
        bitdic = BitDic(tx_seed, self.name + 't', new_vkdic, self.nov)
        bitdic.conversion = tx
        bitdic.parent = self
        return bitdic

    def add_clause(self, vk=None):
        perf_count["add_clause"] += 1
        # add clause c into bit-dict

        def add_vk(self, vkn):
            vclause = self.vkdic[vkn]
            length = len(vclause.dic)
            lst = self.ordered_vkdic.setdefault(length, [])
            if vkn not in lst:
                lst.append(vclause.kname)
            if length == 0:
                # when klause is empty, it is in every bit-value
                for b in self.dic:
                    self.dic[b][0].append(vkn)
                    self.dic[b][1].append(vkn)
            else:
                for bit, v in vclause.dic.items():
                    # bit: bit-position, v: 0 or 1
                    # lst: [[<0-valued cs>],[<1-cs>]]
                    lst = self.dic.get(bit, [[], []])
                    if vkn not in lst[v]:  # v is bit-value: 0 or 1
                        # put vkn in 0-list, or 1-list
                        lst[v].append(vkn)
                return vclause

        if vk:
            return add_vk(self, vk)
        else:
            for vkn in self.vkdic:
                add_vk(self, vkn)
            return self

    def visualize(self):
        self.vis.output(self)


def make_initial_bitdic(conf_filename):
    sdic = get_sdic(conf_filename)
    vkdic = make_vkdic(sdic['kdic'], sdic['nov'])
    bitdic = BitDic("C001", "Org", vkdic, sdic['nov'])
    return bitdic


def test():
    bdic = make_initial_bitdic('config1.json')
    bdic.visualize()

    # split into 2: bdic0(bit-7 = 0) / bdic1(bit-7 = 1)
    # Tx (bdic1) -> bdic1t
    bdic0, bdic1, bdic1t = bdic.split_topbit()
    bdic0.visualize()
    bdic1.visualize()
    bdic1t.visualize()


if __name__ == '__main__':
    test()
    x = 1
