from comm import *

# Data Access Pattern
"""
daps is a list of access patterns.
A program is constructed with phases.  Each phase has their access pattern.
Each access pattern is a set of structs (access pattern entries).  The entry
structs contains memory region, randomness, stride, and number of accesses.

For example,
```
for (i = 0; i < 100; i++) {
    a[i] = 0;
    if (i % 10 == 0)
        b[random() % sizeof(b)] = 1;
    if (i % 20 == 0)
        c[i] = 1;
}
```
becomes pattern below.
```
&a[0]-&a[100], sequential, 1, 100
&b[0]-&b[100], random, 10, 10
&c[0]-&c[100], sequential, 20, 5
```
"""
class Dape:
    saddr = 0
    eaddr = 0
    pattern = "sequential"
    stride = 64
    nr_accs = 100
    prob = 100.0    # Probability of this entry execution
    last_access = -1

    def __init__(self, saddr, eaddr, pattern, stride, nr_accesses, prob=100):
        self.saddr = saddr
        self.eaddr = eaddr
        self.pattern = pattern
        self.stride = stride
        self.nr_accs = nr_accesses
        self.prob = prob
        self.last_access_addr = saddr

def dape_calc_probs(dapes):
    total_nr_accs = 0
    for dape in dapes:
        total_nr_accs += dape.nr_accs
    total_prob = 0.0
    for dape in dapes:
        prob = float(dape.nr_accs) / total_nr_accs
        total_prob += prob
        dape.prob = total_prob
    return total_nr_accs

daps =  [
            [
                Dape(0, SZ_PAGE * 4 - 1, "sequential", 1, 1000000),
                Dape(SZ_PAGE * 4, SZ_PAGE * 8 - 1, "random", 10, 100000),
                Dape(SZ_PAGE * 8, SZ_PAGE * 10 - 1, "sequential", 20, 50000)
            ]
        ]

def file_to_daps(fpath):
    daps = []
    dap = None
    with open(fpath, 'r') as f:
        for l in f:
            print "line: ", l
            if l.startswith('#'):
                continue
            if l == '\n':
                if dap:
                    daps.append(dap)
                dap = None
                continue
            if not dap:
                dap = []
            fields = l.split(',')
            region = fields[0].split('-')
            dap.append(Dape(int(region[0]), int(region[1]), fields[1].strip(),
                int(fields[2]), int(fields[3])))
    if dap:
        daps.append(dap)
    return daps

import sys
if __name__ == "__main__":
    print file_to_daps(sys.argv[1])
