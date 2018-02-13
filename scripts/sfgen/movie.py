from sfgen import *

class RenderMovie(object):
    def __init__(self, name):
        self.name = name
        self.replay = LatticeReplay(name)

    def run(self):
        print "run"
        if not os.path.exists("frames"):
            print "***making folder***"
            os.mkdir("frames")
        self.scan_replays()
        print self.replays
        j=0
        for fn in self.replays:
            j=j+1
            print "loading", fn
            f = open(fn)
            self.current_replay = pickle.load(f)
            print "assigning args"
            kw = {}
            kw["environment"] = self.current_replay.environment
            kw["max_steps"] = self.current_replay.max_steps
            kw["margin"] = self.current_replay.margin
            kw["datalog"] = self.current_replay.datalog
            kw["debug"] = self.current_replay.debug
            cl = CrystalLattice(self.current_replay.size, **kw)
            print "rendering", fn
            ifn="%d.png" % j
            cl.save_image(ifn)
        #x = iter(self.replay)
        #for (idx, frame) in enumerate(self.replay):
        #    fn = "frames/%s_%09d.png" % (self.name, idx + 1)
        #    frame.save_image(fn)

    def scan_replays(self):
        print "scan_replays"
        replays = []
        fn_re = re.compile("cell_log_(\d+).pickle")
        for fn in os.listdir('.'):
            m = fn_re.search(fn)
            if m:
                step = int(m.group(1))
                replays.append((fn, step))
        replays.sort(key=operator.itemgetter(1))
        self.replays = [rp[0] for rp in replays]

        self.replay_map = [rp[1] for rp in replays]
        #print self.replays
        #print self.replay_map

class LatticeReplay(object):
    class ReplayIterator(object):
        def __init__(self, replay):
            print "__init"
            self.replay = replay
            self.idx = 0

        def next(self):
            print "next"
            try:
                lattice = self.replay.get_lattice(self.idx)
                self.idx += 1
                return lattice
            except IndexError:
                raise StopIteration

    def __init__(self, name):
        print "init2"
        self.name = name
        self.current_frame = None
        self.current_replay = None
        pfn = "%s.pickle" % self.name
        self.lattice = CrystalLattice.load_lattice(pfn)
        self.scan_replays()

    def __iter__(self):
        print "__iter"
        return self.ReplayIterator(self)

    def get_lattice(self, step):
        print "get_lattice"
        (step, dm, cm) = self.get_step(step)
        for (idx, cell) in enumerate(zip(dm, cm)):
            self.lattice.cells[idx].diffusive_mass = cell[0]
            self.lattice.cells[idx].crystal_mass = cell[1]
            self.lattice.cells[idx].attached = bool(cell[1])
        for cell in self.lattice.cells:
            cell.update_boundary()
        return self.lattice

    def get_step(self, step):
        print "get_step"
        idx = bisect.bisect_left(self.replay_map, step + 1)
        if self.current_frame != idx or not self.current_replay:
            self.current_frame = idx
            fn = self.replays[self.current_frame]
            print "loading", fn
            f = open(fn)
            self.current_replay = pickle.load(f)
        #offset = self.current_replay[0][0]
        #offset = 0
        #return self.current_replay[step - offset]
        print self.current_replay
        return self.current_replay

    def scan_replays(self):
        print "scan_replays"
        replays = []
        fn_re = re.compile("cell_log_(\d+).pickle")
        for fn in os.listdir('.'):
            m = fn_re.search(fn)
            if m:
                step = int(m.group(1))
                replays.append((fn, step))
        replays.sort(key=operator.itemgetter(1))
        self.replays = [rp[0] for rp in replays]

        self.replay_map = [rp[1] for rp in replays]
        #print self.replays
        #print self.replay_map



