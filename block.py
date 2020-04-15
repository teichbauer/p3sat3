
class BGroup:
    def __init__(self, stv, noc, nob, bso, cig):
        ''' stv: start position
            noc: number of coverlines per block
            nob: number of blocks in this group
            bso: block offset - dist btwn tarts of 2 blocks
            cig: number of cover-liners inside group
            '''
        self.stv = stv
        self.noc = noc
        self.nob = nob
        self.bso = bso
        self.cig = cig
        self.reset()

    def reset(self):
        self.avail = self.cig
        self.position = -1
        self.b_cursor = 0
        self.c_cursor = 0
        self.last = self.stv + (self.nob - 1) * self.bso + self.noc - 1

    def inme(self, pos):
        outside = pos < self.stv or pos > self.last
        return not outside

    def hit(self, pos):
        offset = pos - self.stv
        bi = self.b_cursor
        while bi < self.nob and bi * self.bso <= offset:
            if (bi * self.bso + self.noc) < offset:
                bi += 1
            else:
                self.hit_info = bi, offset % self.bso
                return True
        return False

    def offer(self, pos):
        '''from pos to next cl-pos without a gap - 
           how many cls can be offered as a continuous cl-block
           '''
        get_hit = self.hit(pos)
        if get_hit:
            return self.noc - self.hit_info[1]
        else:
            return 0

    def consume(self, pos):
        """ till v=pos, update avail: take away/use clover-lines, 
            and reset hit_info 
            """
        self.position = pos
        if pos > self.last:
            consumption = self.avail
            self.avail = 0
            return consumption, True
        else:
            consumption = 0
            offset = pos - self.stv
            while self.b_cursor < self.nob:
                bstart = self.b_cursor * self.bso  # bstart rel to self.stv
                if offset >= bstart + self.noc:    # pos jumped over bi-block
                    self.b_cursor += 1             # add what's avail in block
                    consumption += self.noc - self.c_cursor
                    self.c_cursor = 0
                else:      # --------------------  pos lands inside
                    if offset > bstart and offset < (bstart + self.noc):
                        # inside the cover-lines range
                        self.c_cursor = offset - bstart
                        consumption += self.c_cursor
                    break  # -------------------- no need to go next block
            self.avail -= consumption
            return consumption, False


class SuperBGroup:
    def __init__(self, stv, gso, grplst):
        self.stv = stv
        self.gso = gso
        self.glst = grplst
        self.cis = len(grplst) * grplst[0].cig
        self.avail = self.cis
        self.g_cursor = 0
        self.position = -1
        self.last = self.stv + len(grplst) * self.gso - 1

    def inme(self, pos):
        return pos < self.stv or pos > self.last

    def hit(self, pos):
        self.hit_gindex = -1
        for gindex, g in enumerate(self.glst):
            if not g.inme(pos) or g.avail <= 0 or not g.hit(pos):
                continue
            else:
                self.hit_gindex = gindex
                return True
        return None

    def offer(self, pos):
        hit = self.hit(pos)
        if hit:
            return self.glst[self.hit_gindex].offer(pos)
        return 0

    def consume(self, newpos):
        if newpos < self.stv:
            return 0, False
        self.position = newpos
        if newpos > self.last:      # over last value of this super-group
            consumption = self.avail
            self.avail = 0
            next = True             # go to next super-group
        else:  # -------------------- still within this super-group
            consumption = 0         # find the hit group inside this s-group
            gi = self.g_cursor      #
            next = True
            while gi < len(self.glst) and next:
                g = self.glst[gi]
                consum, next = g.consume(newpos)
                consumption += consum
                gi += 1
            self.avail -= consumption
        return consumption, next
