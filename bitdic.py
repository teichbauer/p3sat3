
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

    def __init__(self, kdic, number_of_variables):   # O(m)
        self.nov = number_of_variables
        self.dic = {}
        self.kdic = kdic
        for i in range(number_of_variables):  # number_of_variables ,_ config
            self.dic[i] = [[], []]

    def add_clause(self, c=None):
        # add clause c into bit-dict
        def add_c(self, c):
            clause = self.kdic[c]
            for k, v in clause.items():  # k: bit position, v: 0 or 1
                # lst: [[<0-valued cs>],[<1-cs>]]
                lst = self.dic.get(k, [[], []])
                if c not in lst[v]:  #
                    lst[v].append(c)
            return clause

        if c:
            return add_c(self, c)
        else:
            for cn in self.kdic:
                add_c(self, cn)
            return self

    def sort_clauses(self,              # Complexity: O(m**2)
                     kdic_tobe_sorted,
                     reverse=False,
                     filter_clauses=None):
        """ after wipe out (0-replacing) the bits from filter_clauses,
            if not given, use {0 0 0} for the highst 3 bits, sort the clauses 
            in tobe_sorted, according to the values: bigger -> small, namely, 
            near to highst ->far to highst
            """
        if filter_clauses:
            pass

        lst = []
        for kn in kdic_tobe_sorted:
            clause = self.kdic[kn]
            kvalue = klause_value(clause)
            ind = -1
            for i, e in enumerate(lst):
                # find the first element with bigger kvalue, set index.
                if kvalue < e[1]:
                    ind = i   # set insert position
                    break     # Done the the loop
            lst.insert(ind, (kn, kvalue))
        # lst is ascending order: front klause sit furtherst to
        # the right (0-bit), or furtherst from C001, which is
        # on the leftest/highst 3 bits (for n=8, on bit 7, 6, 5)
        # -----------------------------------------------------------
        # reversed or not?
        if reverse:
            lst.reverse()

        return lst

    def output(self, filename, cselect=[]):
        if len(filename) > 0:
            ofile = open(filename, 'w')
        else:
            ofile = None

        nov = len(self.dic)  # 8
        lines = []
        line = '       '
        for i in range(nov-1, -1, -1):
            line += f'{i}   '
        lines.append(line)
        lines.append('     ' + '-'*(4*nov))

        for cn, c in self.kdic.items():
            line = f'{cn}   '
            bits = list(self.dic.keys())
            bits.reverse()
            for b in bits:
                if b in c:
                    if cn in self.dic[b][0]:
                        line += '0   '
                    elif cn in self.dic[b][1]:
                        line += '1   '
                    else:
                        print(f'{cn} conflict with bit{b}')
                else:
                    line += '    '
            if len(cselect) == 0 or cn in cselect:
                lines.append(line)
        for line in lines:
            if ofile:
                ofile.write(line + '\n')
            else:
                print(line)
