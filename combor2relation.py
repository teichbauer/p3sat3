from basics import get_setlst, klause_value


class Combo2Relation:
    def __init__(self, kdic, nov):
        self.nov = nov
        self.kdic = {}  # kname keyed klauses
        self.compatidic = {}
        self.countdic = {}
        for name, klause in kdic.items():
            self.kdic[name] = {int(b): kl for b, kl in klause.items()}
        # self.kdic = {int(k): v for k, v in config_dic['kdic'].items()}
        # 2-combo-dic (key: sorted tuple as dic-key):
        # {<key>: ('c1' | 'c2' | 'nc' | 'p1' | 'p2' | 'p3')}
        self.bitdic = BitDic(self.kdic, self.nov)
        self.dic = self.reldic_2set(kdic)
        self.set_compatidic()               # O(m**2)

    def sorted_kns(self, reverse):  # Complexity: O(m**2) < bitdic.sort_clauses
        ''' kns from kdic.keys() - knames.
            sorted:  furtherst away from C001 front;
            reverse: nearst to C001
            '''
        klst = self.bitdic.sort_clauses(list(self.kdic.keys()), reverse)
        kns = [e[0] for e in klst]
        return kns

    def set_compatidic(self):           # Complexity: O(m**2)
        names = list(self.kdic.keys())  # O(m)
        for name in names:              # O(m**2)
            kompat_dic = self.compatidic.setdefault(name, {})
            kompat_dic['conflicts'] = []
            for kn in names:
                if kn == name:
                    continue
                ty = self.get_r2_type([name, kn])
                if ty.count('p') == 0:
                    kompat_dic[kn] = self.get_type_RR(ty)
                else:
                    kompat_dic['conflicts'].append(kn)

    def set_countdic(self):
        pass

    def reldic_2set(self, kdic):  # Complexity: O(m**2).
        ''' possible relationship-types between every pair:
            p (p1,p2,p3), n(nc), c1 or c2
            returns a relationship-dic keyed by 2-set (sorted)tuple
            looking like {('C002','C008'): 'p1', ('C009','C012'):'c2',...}
            '''
        dic = {}
        # C(38,2) = 703 2-combinations out of 38.
        # Complexity: K = 0.5*(n**2 - n), for n=38, K=703: O(**2)
        # 703 2-sets, like [{'C001','C003'},..}
        combo_sets = get_setlst(2, kdic)  # O(m**2)

        for two_name_set in combo_sets:
            rdic = {'op': [], 'co': []}  # counts for smae-bits, op-bits
            lst = sorted(list(two_name_set))
            tp = tuple(lst)
            name1, name2 = lst
            klause1 = kdic[name1]
            klause2 = kdic[name2]
            self.bitdic.add_clause(name1)
            self.bitdic.add_clause(name2)
            # loop thru all bits of the 2 klauses
            # how many bit-overlap - if yes, same/opposite value?
            for ky, va in klause1.items():
                for kk, vv in klause2.items():
                    if ky == kk:
                        if va == vv:
                            cos = rdic.setdefault('co', [])
                            cos.append(ky)
                        else:
                            ops = rdic.setdefault('op', [])
                            ops.append(ky)
            msg = ''
            ops = len(rdic['op'])
            cos = len(rdic['co'])
            if ops == 0:
                if cos == 0:
                    msg = 'nc'       # ty = nc
                else:
                    msg = f'c{cos}'  # ty = c1, or c2
            else:
                msg = f'p{ops}'      # ty = p1, p2 or p3
            dic[tp] = msg   # {(C001,C002): c2, (C001,C004):p1, ...}
        return dic  # relation-type ty for every 2-klause combinations

    def get_r2_type(self, pair):
        ''' get relationship between the 2-clauses/names: p1,p2,p3,c1,c2,nc
            the 2 clause name-pair can be in form of [] () or set, as in
            ['C001','C003'], or ('C001','C003') or {'C001','C003'}
            ------------------------------------------------------'''
        if type(pair) == type(()):
            tk = pair
        elif type(pair) == type([]):
            tk = tuple(sorted(pair))
        elif type(pair) == type(set([])):
            tk = tuple(sorted(list(pair)))
        if tk in self.dic:
            return self.dic[tk]
        else:
            return None

    def get_type_RR(self, ty):
        ''' for nov==8, return
            0 (ty==p*), 4(ty==nc), 8(ty==c1) or 16(ty==c2)
            '''
        if ty == 'nc':
            # in case nov=8, 2**(n-6) = 2**2 = 4
            return 2**(self.nov - 6)
        if ty == 'c1':
            # in case nov=8, 2**(n-5) = 2**2 = 8
            return 2**(self.nov - 5)
        if ty == 'c2':
            # in case nov=8, 2**(n-4) = 2**2 = 16
            return 2**(self.nov - 4)
        # if r2type in ('p1', 'p2', 'p3'):
        return 0

    def get_2RR(self, name_tuple):
        r2type = self.get_r2_type(name_tuple)
        return self.get_type_RR(r2type)

    def get_compatibles(self, knames):
        kn = knames.pop(0)
        dic = self.compatidic[kn]
        dic.pop('conflicts')
        s0 = set(dic.keys())
        for kname in knames:
            d = self.compatidic[kname]
            d.pop('conflicts')
            s = set(d.keys())
            s0 = s0.intersection(s)
        return s0


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        fname = './config1.json'
    else:
        fname = sys.argv[1].strip()
    src = eval(open(fname).read())
    rel2 = Combo2Relation(src['kdic'], src['number_of_variables'])
    x = 1
