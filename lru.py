SZ_PAGE = 4096

# LRU Reclamation Algorithm.
lru_list = []
LRU_MEM_PORTION_TO_EVICT = 0.2
LRU_RECLAIM_RUNTIME = 60

mem_size = None

def lru_reclaim():
    global stat_nr_reclaims
    global lru_list

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
