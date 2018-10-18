#!/usr/bin/env python

# Common
SZ_PAGE = 4096

# stat
stat_nr_reclaims = 0
stat_nr_major_faults = 0
stat_nr_minor_faults = 0
stat_nr_hits = 0

from dap import *

daps =  [
            [
                Dape(0, SZ_PAGE * 4 - 1, "sequential", 1, 1000000),
                Dape(SZ_PAGE * 4, SZ_PAGE * 8 - 1, "random", 10, 100000),
                Dape(SZ_PAGE * 8, SZ_PAGE * 10 - 1, "sequential", 20, 50000)
            ]
        ]



# LRU Reclamation Algorithm.
lru_list = []
LRU_MEM_PORTION_TO_EVICT = 0.2
LRU_RECLAIM_RUNTIME = 60

def lru_reclaim():
    global stat_nr_reclaims
    global lru_list

    stat_nr_reclaims += 1

    nr_pages_to_evict = int(mem_size * LRU_MEM_PORTION_TO_EVICT / SZ_PAGE)
    to_evict = lru_list[-1 * nr_pages_to_evict:]
    lru_list = lru_list[:-1 * nr_pages_to_evict]

    return to_evict, LRU_RECLAIM_RUNTIME

# Hook for page access
def lru_accessed(pfn):
    global lru_list

    if pfn in lru_list:
        lru_list.remove(pfn)
    lru_list = [pfn] + lru_list



import argparse
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

def mmse_alloc_page():
    global available_mem

    runtime = 0
    if available_mem <= 0:
        # memory pressure!
        evicted, runtime = reclaim()
        for pfn in evicted:
            ptes[pfn].evicted = True
        available_mem += SZ_PAGE * len(evicted)
    runtime += mem_page_alloc_latency
    available_mem -= SZ_PAGE

    return runtime

def mmse_access(dape):
    global stat_nr_major_faults
    global stat_nr_minor_faults
    global stat_nr_hits
    global available_mem

    runtime = 0
    target_addr = 0
    if dape.pattern == "sequential":
        target_addr = dape.last_access_addr + dape.stride
        if target_addr >= dape.eaddr:
            target_addr = dape.saddr
            dape.last_access_addr = dape.saddr
    if dape.pattern == "random":
        target_addr = random.randrange(dape.saddr, dape.eaddr)

    pfn = target_addr / 4096

    if not pfn in ptes:
        # minor page fault
        stat_nr_minor_faults += 1
        runtime += mmse_alloc_page()
        available_mem -= SZ_PAGE
        ptes[pfn] = PTE(False)
        runtime += mem_minor_page_fault_latency
    elif ptes[pfn].evicted:
        # major page fault (evicted)
        stat_nr_major_faults += 1
        runtime += mmse_alloc_page()
        available_mem -= SZ_PAGE
        ptes[pfn].evicted = False
        runtime += mem_major_page_fault_latency
    else:
        stat_nr_hits += 1
        # hit!
        pass

    reclaim_hook(pfn)
    runtime += mem_access_latency
    dape.last_access_addr = target_addr

    return runtime

def mmse_runtime(daps):
    runtime = 0
    for dap in daps:
        total_nr_accs = dape_calc_probs(dap)
        nr_accs = 0
        while nr_accs < total_nr_accs:
            runtime += mmse_access(next_entry(dap))
            nr_accs += 1
    return runtime

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # memory characteristics of the target system
    parser.add_argument('--msz', type=int, default=SZ_PAGE * 4,
            metavar='memory_size', help='target system memory size')
    parser.add_argument('--maccess', type=int, default=10,
            metavar='memory_access_latency',
            help='latency of memory access (nsecs)')
    parser.add_argument('--mminorf', type=int, default=2000,
            metavar='minor_fault_latency',
            help='latency of minor fault handling (nsecs)')
    parser.add_argument('--mmajorf', type=int, default=20000,
            metavar='major_fault_latency',
            help='latency of major fault handling (nsecs)')
    parser.add_argument('--mpgalloc', type=int, default=200,
            metavar='page_alloc_latency',
            help='latency of single page allocation (nsecs)')

    args = parser.parse_args()

    mem_size = args.msz
    mem_access_latency = args.maccess
    mem_minor_page_fault_latency = args.mminorf
    mem_major_page_fault_latency = args.mmajorf
    mem_page_alloc_latency = args.mpgalloc

    available_mem = mem_size

    reclaim = lru_reclaim
    reclaim_hook = lru_accessed
    random.seed(42)
    print "runtime: ", mmse_runtime(daps), "nsecs"
    print "\n"

    print "statistics"
    print "=========="
    print ""
    print "reclaims: ", stat_nr_reclaims
    print "minor_faults: ", stat_nr_minor_faults
    print "major_faults: ", stat_nr_major_faults
    print "hits: ", stat_nr_hits
