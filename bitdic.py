from basics import get_sdic
from vklause import VKlause
from visualizer import Visualizer
from TransKlauseEngine import make_vkdic, trans_vkdic


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
        self.seed_name = seed_name
        self.name = bdname
        self.nov = nov
        self.dic = {}   # keyed by bits, value: [[0-kns],[1-kns]]
        self.vkdic = vkdic
        self.parent = None  # the parent that generated / tx-to self
        self.done = False
        if nov <= 5 and vkdic[seed_name].nob == 0:
            self.done = True
        for i in range(nov):        # number_of_variables from config
            self.dic[i] = [[], []]
        self.add_clause()
        self.conversion = None
        self.short_kns = []         # kns with dic length reduced (<3)
        self.vis = Visualizer(self.vkdic, self.nov)

    def split_topbit(self):
        tb = self.nov - 1   # top bit number
        vkdic0 = {}     # vks with top-bit == 0
        vkdic1 = {}     # vks with top-bit == 1
        vkdic_mix = {}  # vks with top-bit not used

        kns = list(self.vkdic.keys())

        for kn in self.dic[tb][0]:
            vklause = self.vkdic[kn]
            # drop top bit, nov decrease by 1 (tp)
            vklause.dic.pop(tb)
            vkdic0[kn] = VKlause(kn, vklause.dic, tb)

        for kn in self.dic[tb][1]:
            vklause = self.vkdic[kn]
            # drop top bit, nov decrease by 1 (tp)
            vklause.dic.pop(tb)
            vkdic1[kn] = VKlause(kn, vklause.dic, tb)

        for kn in kns:
            if kn not in vkdic0 and kn not in vkdic1:
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
        bitdic0.conversion = f'{tb}@0'
        bitdic0.parent = self
        bitdic0.set_short_kns(self.dic[tb][0])

        seed = self.set_txseed(vkdic1)
        if seed == None:
            return self.get_sat(), None
        else:
            bitdic_tmp = BitDic(
                seed,
                self.name + f'-{tb}@1',
                vkdic1,
                tb)
            bitdic_tmp.conversion = f'{tb}@1'
            bitdic_tmp.parent = self
            bitdic_tmp.set_short_kns(self.dic[tb][1])

            # bitdic1 be tx-ed on 1 of its shortkns
            bitdic1 = bitdic_tmp.TxTopKn(seed)
            print(f'for bitdic1t Tx-seed:{seed}')
            return bitdic0, bitdic1

    def get_sat(self):
        if type(self.conversion) == type(''):
            pass
        else:
            pass
        return 234

    def set_short_kns(self, kns):
        self.short_kns = kns

    def set_txseed(self, vkdic):
        ''' pick a kn in vkdic with shortest dic
            '''
        L = 4     # bigger than any klause length, so it will bereplaced
        lst = []  # list of kns with the same shortest length
        for kn in vkdic:
            if vkdic[kn].nob < L:
                L = vkdic[kn].nob
                # remove kns in lst with length > L
                i = 0
                while i < len(lst):
                    if self.vkdic[lst[i]].nob > L:
                        lst.pop(i)
                    else:
                        i += 1
                lst.append(kn)
        # TBD: amng kns in lst, pick 1 based on ..?
        if len(lst) == 0:
            x = 1
            return None
        return lst[0]

    def pick_seed(self):
        L = 3
        seed = ''
        # for kn in self.short_kns:
        for kn in self.vkdic:
            if self.vkdic[kn].nob < L:
                seed = kn
                L = self.vkdic[kn].nob
        return seed, L

    def TxTopKn(self, tx_seed):
        new_vkdic, tx = trans_vkdic(
            self.vkdic,     # tx all vkdic members
            tx_seed,        # seed-kn for Tx
            self.nov,       # nov remains the same
            True)           # Tx-to-top-position: True
        bitdic = BitDic(tx_seed, self.name + 't', new_vkdic, self.nov)
        bitdic.conversion = tx
        bitdic.short_kns = self.short_kns[:]  # shorts have the same names
        bitdic.parent = self
        return bitdic

    def add_clause(self, vk=None):
        # add clause c into bit-dict
        def add_vk(self, vkn):
            vclause = self.vkdic[vkn]
            for bit, v in vclause.dic.items():  # bit: bit-position, v: 0 or 1
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
