from basics import get_sdic
from vklause import VKlause
from visualizer import Visualizer
from TransKlauseEngine import TransKlauseEngine, make_vkdic


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

        vkdic0_pure.update(vkdic_mix)
        vkdic1_pure.update(vkdic_mix)
        bitdic0 = BitDic(self.name + '-0', vkdic0_pure, tb)
        bitdic1 = BitDic(self.name + '-1', vkdic1_pure, tb)
        return bitdic0, bitdic1

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
    vkdic = make_vkdic(sdic['kdic'])
    bitdic = BitDic("Org", vkdic, sdic['nov'])
    return bitdic


if __name__ == '__main__':
    bdic = make_bitdic('config1.json')
    bdic0, bdic1 = bdic.split_topbit()
    # bdic.visualize()
    x = 1
