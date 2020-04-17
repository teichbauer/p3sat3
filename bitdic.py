from basics import get_sdic
from vklause import VKlause
from visualizer import Visualizer
from TransKlauseEngine import TransKlauseEngine, make_vkdic, trans_vkdic


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

    def __init__(self, bdname, vkdic, nov):   # O(m)
        self.name = bdname
        self.nov = nov
        self.dic = {}   # keyed by bits, value: [[0-kns],[1-kns]]
        self.vkdic = vkdic
        for i in range(nov):        # number_of_variables from config
            self.dic[i] = [[], []]
        self.add_clause()
        self.coversion_path = []
        self.short_kns = []         # kns with dic length reduced (<3)
        self.vis = Visualizer(self.vkdic, self.nov)

    def split_topbit(self):
        tb = self.nov - 1   # top bit number
        vkdic0_pure = {}    # vks with top-bit == 0
        vkdic1_pure = {}    # vks with top-bit == 1
        vkdic_mix = {}      # vks with top-bit not used

        kns = list(self.vkdic.keys())

        for kn in self.dic[tb][0]:
            vklause = self.vkdic[kn]
            # drop top bit, nov decrease by 1 (tp)
            vklause.dic.pop(tb)
            vkdic0_pure[kn] = VKlause(kn, vklause.dic, tb)

        for kn in self.dic[tb][1]:
            vklause = self.vkdic[kn]
            # drop top bit, nov decrease by 1 (tp)
            vklause.dic.pop(tb)
            vkdic1_pure[kn] = VKlause(kn, vklause.dic, tb)

        for kn in kns:
            if kn not in vkdic0_pure and kn not in vkdic1_pure:
                vklause = self.vkdic[kn]
                # no need to drop top bit, they don't have it.
                vkdic_mix[kn] = VKlause(kn, vklause.dic, tb)

        vkdic0_pure.update(vkdic_mix)  # add mix-dic to 0-dic
        vkdic1_pure.update(vkdic_mix)  # add mix-dic to 1-dic

        bitdic0 = BitDic(self.name + f'-{tb}@0', vkdic0_pure, tb)
        bitdic0.coversion_path.append(f'{tb}@0')
        bitdic0.set_short_kns(self.dic[tb][0])

        bitdic1 = BitDic(self.name + f'-{tb}@1', vkdic1_pure, tb)
        bitdic1.coversion_path.append(f'{tb}@1')
        bitdic1.set_short_kns(self.dic[tb][1])

        # bitdic1 be tx-ed on 1 of its shortkns
        bitdic1t, tx_seed = bitdic1.TxTopKn()
        print(f'for bitdic1t Tx-seed:{tx_seed}')
        return bitdic0, bitdic1, bitdic1t

    def set_short_kns(self, kns):
        self.short_kns = kns

    def TxTopKn(self):
        seed_kn = self.short_kns[0]
        new_vkdic, tx = trans_vkdic(self.vkdic, seed_kn, self.nov, True)
        bitdic = BitDic(self.name + 't', new_vkdic, self.nov)
        bitdic.coversion_path.append(tx)
        return bitdic, seed_kn

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
        self.vis.output(self.name + '.txt')


def make_bitdic(conf_filename):
    sdic = get_sdic(conf_filename)
    vkdic = make_vkdic(sdic['kdic'], sdic['nov'])
    bitdic = BitDic("Org", vkdic, sdic['nov'])
    return bitdic


if __name__ == '__main__':
    bdic = make_bitdic('config1.json')
    # bdic.visualize()
    bdic0, bdic1, bdic1t = bdic.split_topbit()
    bdic0.visualize()
    bdic1.visualize()
    bdic1t.visualize()
    x = 1
