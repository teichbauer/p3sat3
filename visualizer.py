class Visualizer:
    def __init__(self, vkdic, nov):
        self.vkdic = vkdic
        self.nov = nov

    def output_vklause(self, kn):
        klause = self.vkdic[kn].dic
        bits = sorted(list(klause.keys()))
        bits.reverse()
        msg = f'{kn}: ' + '{'
        for b in bits:
            msg += f'{b}:' + str(klause[b]) + '  '
        msg += ' }'
        return msg

    def output_vkdic(self):
        knames = sorted(list(self.vkdic.keys()))
        msg = ''
        for kn in knames:
            msg += self.output_vklause(kn) + '\n'
        # msg += '-'*60 + '\n'
        return knames, msg

    def output(self, filename, tx=None):
        knames, koutput = self.output_vkdic()
        fil = open('./verify/' + filename, 'w')
        fil.write(filename + '\n')
        fil.write('-'*60 + '\n')
        if tx:
            line = 'txn: ' + str(tx.bitname_tx) + ',  '
            line += 'txv: ' + str(tx.bitvalue_tx) + '\n'
            fil.write(line + '\n')
        fil.write(koutput)
        line = '------ '
        for i in range(self.nov):
            line += str(self.nov - i - 1) + '--'
        fil.write(line + '\n')
        for v in range(2**self.nov):
            head = str(v).zfill(5) + ': '
            msg = '  '.join(list(bin(v)[2:].zfill(self.nov)))
            line = head + msg + ' $ '
            for kn in knames:
                if self.vkdic[kn].hit(v):
                    line += f'{kn} '
            fil.write(line + '\n')
        fil.close()
