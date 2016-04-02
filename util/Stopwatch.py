import time


class Stopwatch(object):
    _events = None

    def __init__(self, name='Generic stopwatch'):
        self._t_start = None
        self._name = name
        self.start()
        
    def start(self):
        self._events = []
        self._t_start = time.time()
        self._events.append((0, '__start'))
    
    def event(self, description):
        self._events.append((time.time() - self._t_start, description))
    
    def elapsed(self):
        return time.time() - self._t_start

    def lap(self):
        return time.time() - self._t_start + self._events[-1][0]
    
    def reset(self):
        self.start()
    
    def report(self):
        print "\nTimings for {}".format(self._name)
        for n in xrange(len(self._events)):
            if n == 0:
                continue
            this = self._events[n]
            prev = self._events[n-1]
            print "{ts:.2f}s ({dur:.2f}s): {descr}" \
                .format(ts=this[0],
                        dur=this[0]-prev[0],
                        descr=this[1])
