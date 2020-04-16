from basics import get_sdic
from vklause import VKlause
from visualizer import Visualizer


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
        self.vis = Visualizer(self.vkdic, self.nov)

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
    vkdic = {}
    for kn, d in sdic['kdic'].items():
        vkdic[kn] = VKlause(kn, d, sdic['nov'])
    bitdic = BitDic("Org", vkdic, sdic['nov'])
    return bitdic


if __name__ == '__main__':
    bdic = make_bitdic('config1.json')
    bdic.visualize()
    x = 1
