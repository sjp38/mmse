from comm import *

# FIFO Reclamation Algorithm.
fifo_list = []
FIFO_MEM_PORTION_TO_EVICT = 0.2
FIFO_RECLAIM_RUNTIME = 20

mem_size = None

def reclaim():
    global fifo_list

    nr_pages_to_evict = int(mem_size * FIFO_MEM_PORTION_TO_EVICT / SZ_PAGE)
    to_evict = fifo_list[-1 * nr_pages_to_evict:]
    lru_list = fifo_list[:-1 * nr_pages_to_evict]

    return to_evict, FIFO_RECLAIM_RUNTIME

# Hook for page access
def accessed(pfn):
    global fifo_list

    if not pfn in fifo_list:
        fifo_list = [pfn] + fifo_list
