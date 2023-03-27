from cache_sim import CacheSim

ADDRESS_SIZE = 16
CACHE_SIZE = 1024
BLOCK_SIZE = 64
ASSOCIATIVITY = 1
WRITE_BACK = True

cache_sim = CacheSim(ADDRESS_SIZE, CACHE_SIZE, BLOCK_SIZE, ASSOCIATIVITY, WRITE_BACK)

cache_sim.read(0)
cache_sim.read(32)
cache_sim.read(1024)
cache_sim.write(1024, 4)
cache_sim.read(1024)
cache_sim.write(32, 12)
cache_sim.read(32)
