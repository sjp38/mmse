#!/usr/bin/env python

# Memory characteristics
mem_size = 1024 * 1024 * 1024
hit_latency = 10    # nano second
miss_latency = 20000 # nano second

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
class dape:
    region = [0, 0]
    pattern = "sequential"
    stride = 64
    nr_accs = 100
    prob = 100.0    # Probability of this entry execution

    def __init__(self, saddr, eaddr, pattern, stride, nr_accesses, prob):
        self.region = [saddr, eaddr]
        self.pattern = pattern
        self.stride = stride
        self.nr_accs = nr_accesses
        self.prob = prob


# Reclamation Algorithm.  Simulate data access pattern and return regions to be
# evicted.
def reclaim(daps):
    return []

if __name__ == "__main__":
    print "hello"
