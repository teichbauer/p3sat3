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
        msg += '-'*60 + '\n'
        return knames, msg

    def output(self, filename):
        knames, koutput = self.output_vkdic()
        fil = open('./verify/' + filename, 'w')
        fil.write(koutput)
        for v in range(2**self.nov):
            line = str(v).zfill(4) + ': '
            for kn in knames:
                if self.vkdic[kn].hit(v):
                    line += f'{kn} '
            fil.write(line + '\n')
        fil.close()
