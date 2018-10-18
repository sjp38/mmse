#!/usr/bin/env python

# Common
SZ_PAGE = 4096

# stat
stat_nr_reclaims = 0
stat_nr_major_faults = 0
stat_nr_minor_faults = 0
stat_nr_hits = 0


# Memory characteristics
mem_size = SZ_PAGE * 4
mem_access_latency = 10    # nano second
mem_minor_page_fault_latency = 2000
mem_major_page_fault_latency = 20000

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
        self.last_access_addr = -1

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
                Dape(0, SZ_PAGE * 4 - 1, "sequential", 1, 10000),
                Dape(SZ_PAGE * 4, SZ_PAGE * 8 - 1, "random", 10, 1000),
                Dape(SZ_PAGE * 8, SZ_PAGE * 10 - 1, "sequential", 20, 500)
            ]
        ]



# LRU Reclamation Algorithm.
lru_list = []
LRU_MEM_PORTION_TO_EVICT = 0.2

def lru_reclaim():
    global stat_nr_reclaims
    global lru_list

    stat_nr_reclaims += 1

    nr_pages_to_evict = int(mem_size * LRU_MEM_PORTION_TO_EVICT / SZ_PAGE)
    to_evict = lru_list[-1 * nr_pages_to_evict:]
    lru_list = lru_list[:-1 * nr_pages_to_evict]

    return to_evict

# Hook for page access
def lru_accessed(pfn):
    global lru_list

    if pfn in lru_list:
        lru_list.remove(pfn)
    lru_list = [pfn] + lru_list



import random

def next_entry(dap):
    luck = random.uniform(0, 1)
    for dape in dap:
        if luck < dape.prob:
            return dape

class PTE:
    evicted = False

    def __init__(self, evicted):
        self.evicted = evicted

ptes = {}

available_mem = mem_size

def demu_access(dape):
    global stat_nr_major_faults
    global stat_nr_minor_faults
    global stat_nr_hits
    global available_mem

    runtime = 0
    target_addr = 0
    if dape.pattern == "sequential":
        target_addr = dape.last_access_addr + dape.stride
    if dape.pattern == "random":
        target_addr = random.randrange(dape.saddr, dape.eaddr)

    pfn = target_addr / 4096

    # memory pressure!
    if available_mem <= 0:
        evicted = reclaim()
        for pfn in evicted:
            ptes[pfn].evicted = True
        available_mem += SZ_PAGE * len(evicted)

    if not pfn in ptes:
        # minor page fault
        stat_nr_minor_faults += 1
        ptes[pfn] = PTE(False)
        runtime += mem_minor_page_fault_latency
        available_mem -= SZ_PAGE
    elif ptes[pfn].evicted:
        # major page fault (evicted)
        stat_nr_major_faults += 1
        ptes[pfn].evicted = False
        runtime += mem_major_page_fault_latency
        available_mem -= SZ_PAGE
    else:
        stat_nr_hits += 1
        # hit!
        pass

    reclaim_hook(pfn)
    runtime += mem_access_latency

    return runtime

def demu_runtime(daps):
    runtime = 0
    for dap in daps:
        total_nr_accs = dape_calc_probs(dap)
        nr_accs = 0
        while nr_accs < total_nr_accs:
            runtime += demu_access(next_entry(dap))
            nr_accs += 1
    return runtime

if __name__ == "__main__":
    reclaim = lru_reclaim
    reclaim_hook = lru_accessed
    random.seed(42)
    print "runtime: ", demu_runtime(daps), "nsecs"

    print "reclaims: ", stat_nr_reclaims
    print "minor faults: ", stat_nr_minor_faults
    print "major faults: ", stat_nr_major_faults
    print "hits: ", stat_nr_hits
